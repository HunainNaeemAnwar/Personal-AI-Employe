/**
 * Gmail Client for Email Sending
 *
 * Handles Gmail API authentication, email composition, and sending with retry logic.
 */

import { google } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';
import * as fs from 'fs';
import * as path from 'path';

interface SendEmailParams {
  recipients: string[];
  subject: string;
  body: string;
  cc?: string[];
  bcc?: string[];
  threadId?: string;
  inReplyTo?: string;
}

interface SendEmailResult {
  messageId: string;
  threadId?: string;
}

/**
 * Gmail Client for sending emails via Gmail API
 */
export class GmailClient {
  private credentialsPath: string;
  private tokenPath: string;
  private oauth2Client: OAuth2Client | null = null;
  private maxRetries: number;
  private retryBackoffBase: number;

  constructor(credentialsPath: string, tokenPath: string) {
    this.credentialsPath = credentialsPath;
    this.tokenPath = tokenPath;
    this.maxRetries = parseInt(process.env.MAX_RETRY_ATTEMPTS || '3', 10);
    this.retryBackoffBase = parseInt(process.env.RETRY_BACKOFF_BASE || '1000', 10);
  }

  /**
   * Authenticate with Gmail API using OAuth2
   */
  private async authenticate(): Promise<OAuth2Client> {
    if (this.oauth2Client) {
      return this.oauth2Client;
    }

    // Load credentials
    const credentialsContent = fs.readFileSync(this.credentialsPath, 'utf-8');
    const credentials = JSON.parse(credentialsContent);

    const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;

    this.oauth2Client = new google.auth.OAuth2(
      client_id,
      client_secret,
      redirect_uris[0]
    );

    // Load token
    if (!fs.existsSync(this.tokenPath)) {
      throw new Error(
        `Token file not found: ${this.tokenPath}. Please run the watcher first to authenticate.`
      );
    }

    const tokenContent = fs.readFileSync(this.tokenPath, 'utf-8');
    const token = JSON.parse(tokenContent);

    this.oauth2Client.setCredentials(token);

    // Check if token needs refresh
    const tokenInfo = await this.oauth2Client.getTokenInfo(token.access_token);
    const expiryDate = tokenInfo.expiry_date || 0;

    if (Date.now() >= expiryDate) {
      console.error('Token expired, refreshing...');
      const { credentials: newCredentials } = await this.oauth2Client.refreshAccessToken();
      this.oauth2Client.setCredentials(newCredentials);

      // Save refreshed token
      fs.writeFileSync(this.tokenPath, JSON.stringify(newCredentials, null, 2));
      console.error('Token refreshed successfully');
    }

    return this.oauth2Client;
  }

  /**
   * Create RFC 2822 formatted email message
   */
  private createEmailMessage(params: SendEmailParams): string {
    const { recipients, subject, body, cc, bcc, threadId, inReplyTo } = params;

    const headers: string[] = [];

    // To header
    headers.push(`To: ${recipients.join(', ')}`);

    // CC header
    if (cc && cc.length > 0) {
      headers.push(`Cc: ${cc.join(', ')}`);
    }

    // BCC header
    if (bcc && bcc.length > 0) {
      headers.push(`Bcc: ${bcc.join(', ')}`);
    }

    // Subject header
    headers.push(`Subject: ${subject}`);

    // Threading headers
    if (inReplyTo) {
      headers.push(`In-Reply-To: ${inReplyTo}`);
      headers.push(`References: ${inReplyTo}`);
    }

    // Content-Type header
    headers.push('Content-Type: text/plain; charset=utf-8');

    // Combine headers and body
    const message = headers.join('\r\n') + '\r\n\r\n' + body;

    // Encode to base64url format (Gmail API requirement)
    return Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
  }

  /**
   * Send email with retry logic
   */
  async sendEmail(params: SendEmailParams): Promise<SendEmailResult> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        // Authenticate
        const auth = await this.authenticate();

        // Create Gmail API client
        const gmail = google.gmail({ version: 'v1', auth });

        // Create email message
        const encodedMessage = this.createEmailMessage(params);

        // Send email
        const response = await gmail.users.messages.send({
          userId: 'me',
          requestBody: {
            raw: encodedMessage,
            threadId: params.threadId,
          },
        });

        // Log successful send
        this.logEmailSent({
          messageId: response.data.id || 'unknown',
          threadId: response.data.threadId,
          recipients: params.recipients,
          subject: params.subject,
          timestamp: new Date().toISOString(),
        });

        return {
          messageId: response.data.id || 'unknown',
          threadId: response.data.threadId,
        };
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));

        // Check if error is retryable
        const isRetryable = this.isRetryableError(error);

        if (!isRetryable || attempt === this.maxRetries - 1) {
          // Non-retryable error or last attempt - throw immediately
          throw this.enhanceError(lastError, attempt + 1);
        }

        // Calculate backoff delay (exponential: 1s, 2s, 4s)
        const delay = this.retryBackoffBase * Math.pow(2, attempt);

        console.error(
          `[Retry ${attempt + 1}/${this.maxRetries}] Email send failed: ${lastError.message}. Retrying in ${delay}ms...`
        );

        // Wait before retry
        await this.sleep(delay);
      }
    }

    // All retries exhausted
    throw this.enhanceError(
      lastError || new Error('Unknown error'),
      this.maxRetries
    );
  }

  /**
   * Check if error is retryable
   */
  private isRetryableError(error: any): boolean {
    // Network errors are retryable
    if (error.code === 'ECONNRESET' || error.code === 'ETIMEDOUT' || error.code === 'ENOTFOUND') {
      return true;
    }

    // Rate limit errors are retryable
    if (error.code === 429 || (error.response && error.response.status === 429)) {
      return true;
    }

    // Server errors (5xx) are retryable
    if (error.response && error.response.status >= 500) {
      return true;
    }

    // Auth errors are NOT retryable (need manual intervention)
    if (error.code === 401 || (error.response && error.response.status === 401)) {
      return false;
    }

    // Validation errors are NOT retryable
    if (error.code === 400 || (error.response && error.response.status === 400)) {
      return false;
    }

    // Default: retry
    return true;
  }

  /**
   * Enhance error with retry context
   */
  private enhanceError(error: Error, attempts: number): Error {
    const enhancedError = new Error(
      `Failed to send email after ${attempts} attempt(s): ${error.message}`
    );
    enhancedError.stack = error.stack;
    return enhancedError;
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Log sent email to file
   */
  private logEmailSent(logEntry: {
    messageId: string;
    threadId?: string;
    recipients: string[];
    subject: string;
    timestamp: string;
  }): void {
    try {
      const logPath = process.env.EMAIL_LOG_PATH || '/Logs/email_sent.log';
      const logDir = path.dirname(logPath);

      // Create log directory if it doesn't exist
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }

      // Append log entry
      const logLine = JSON.stringify(logEntry) + '\n';
      fs.appendFileSync(logPath, logLine);

      console.error(`Email sent successfully: ${logEntry.messageId}`);
    } catch (error) {
      console.error('Failed to write email log:', error);
      // Don't throw - logging failure shouldn't fail the email send
    }
  }
}
