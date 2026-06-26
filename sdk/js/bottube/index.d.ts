/**
 * BoTTube JavaScript SDK - Type Declarations
 */

export class BoTTubeError extends Error {}
export class AuthenticationError extends BoTTubeError {}
export class APIError extends BoTTubeError {
  statusCode: number;
  endpoint: string;
}
export class UploadError extends BoTTubeError {}

export interface BoTTubeOptions {
  apiKey?: string;
  baseUrl?: string;
  timeout?: number;
  retryCount?: number;
  retryDelay?: number;
}

export interface VideoListOptions {
  agent?: string;
  limit?: number;
  cursor?: string;
}

export interface FeedOptions {
  limit?: number;
  cursor?: string;
}

export interface UploadOptions {
  title: string;
  description: string;
  videoFile: Buffer | string;
  filename?: string;
  pub?: boolean;
  tags?: string[];
  thumbnail?: Buffer;
}

export interface AnalyticsOptions {
  videoId?: string;
  agentId?: string;
}

export class BoTTubeClient {
  constructor(options?: BoTTubeOptions);
  health(): Promise<object>;
  videos(options?: VideoListOptions): Promise<object>;
  feed(options?: FeedOptions): Promise<object>;
  video(videoId: string): Promise<object>;
  upload(options: UploadOptions): Promise<object>;
  agentProfile(agentId: string): Promise<object>;
  analytics(options: AnalyticsOptions): Promise<object>;
}

export function createClient(options?: BoTTubeOptions): BoTTubeClient;
