/**
 * Email Sender MCP Server
 *
 * Provides email sending capability via Gmail API through the Model Context Protocol.
 * Supports OAuth2 authentication, retry logic, and proper email threading.
 */

import { McpServer, StdioServerTransport } from '@modelcontextprotocol/server';
import { z } from 'zod';
import * as dotenv from 'dotenv';
import { GmailClient } from './gmail-client.js';
import type { CallToolResult } from '@modelcontextprotocol/server';

// Load environment variables
dotenv.config();

// Zod schema for send_email tool input
const SendEmailInputSchema = z.object({
  recipients: z.array(z.string().email()).min(1, 'At least one recipient required'),
  subject: z.string().min(1, 'Subject is required'),
  body: z.string().min(1, 'Body is required'),
  cc: z.array(z.string().email()).optional(),
  bcc: z.array(z.string().email()).optional(),
  threadId: z.string().optional(),
  inReplyTo: z.string().optional(),
});

// Zod schema for send_email tool output
const SendEmailOutputSchema = z.object({
  success: z.boolean(),
  messageId: z.string().optional(),
  threadId: z.string().optional(),
  error: z.string().optional(),
  timestamp: z.string(),
});

/**
 * Initialize and run the Email Sender MCP Server
 */
async function main() {
  // Validate required environment variables
  const credentialsPath = process.env.GMAIL_CREDENTIALS_PATH;
  const tokenPath = process.env.GMAIL_TOKEN_PATH;

  if (!credentialsPath || !tokenPath) {
    throw new Error('GMAIL_CREDENTIALS_PATH and GMAIL_TOKEN_PATH must be set');
  }

  // Initialize Gmail client
  const gmailClient = new GmailClient(credentialsPath, tokenPath);

  // Create MCP server
  const server = new McpServer(
    {
      name: 'email-sender',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Register send_email tool
  server.registerTool(
    'send_email',
    {
      title: 'Send Email',
      description: 'Send an email via Gmail API with support for threading, CC/BCC, and retry logic',
      inputSchema: SendEmailInputSchema,
      outputSchema: SendEmailOutputSchema,
    },
    async (input): Promise<CallToolResult> => {
      try {
        // Send email via Gmail client
        const result = await gmailClient.sendEmail(input);

        // Return success response
        const output = {
          success: true,
          messageId: result.messageId,
          threadId: result.threadId,
          timestamp: new Date().toISOString(),
        };

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(output, null, 2),
            },
          ],
          structuredContent: output,
        };
      } catch (error) {
        // Return error response
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';

        const output = {
          success: false,
          error: errorMessage,
          timestamp: new Date().toISOString(),
        };

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(output, null, 2),
            },
          ],
          structuredContent: output,
          isError: true,
        };
      }
    }
  );

  // Setup error handling
  server.onerror = (error) => {
    console.error('[MCP Error]', error);
  };

  // Setup graceful shutdown
  process.on('SIGINT', async () => {
    await server.close();
    process.exit(0);
  });

  // Connect server via stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Email Sender MCP server running on stdio');
}

// Start server
main().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});
