import axios from 'axios';
import { z } from 'zod';

// Схемы данных для гразера и наград
const GrazerEngagementSchema = z.object({
  userId: z.string(),
  metrics: z.object({
    posts: z.number(),
    comments: z.number(),
    uploads: z.number(),
    upvotes_received: z.number(),
  }),
  epoch: z.number(),
});

const RewardDistributionSchema = z.object({
  userId: z.string(),
  totalReward: z.number(),
  breakdown: z.object({
    postReward: z.number(),
    commentReward: z.number(),
    uploadReward: z.number(),
    upvoteReward: z.number(),
  }),
});

export class SocialMiningRewardCalculator {
  private apiBaseUrl: string;
  private axiosInstance: any;

  // Константы наград согласно RIP-310
  private readonly REWARDS = {
    POST: 0.01,
    COMMENT: 0.002,
    UPLOAD: 0.05,
    UPVOTE: 0.001,
  };

  // Лимиты частоты (Caps)
  private readonly CAPS = {
    POSTS: 5,
    COMMENTS: 20,
    UPLOADS: 3,
    UPVOTES: 1000,
  };

  constructor(apiBaseUrl: string, axiosInstance?: any) {
    this.apiBaseUrl = apiBaseUrl;
    this.axiosInstance = axiosInstance || axios;
  }

  /**
   * Расчет награды для одного пользователя за эпоху
   */
  async calculateUserReward(userId: string, epoch: number): Promise<any> {
    try {
      // 1. Получаем метрики из grazer-skill
      const response = await this.axiosInstance.get(`${this.apiBaseUrl}/api/grazer/metrics`, {
        params: { userId, epoch }
      });
      const engagement = GrazerEngagementSchema.parse(response.data);

      // 2. Применяем лимиты и считаем выплаты
      const postReward = Math.min(engagement.metrics.posts, this.CAPS.POSTS) * this.REWARDS.POST;
      const commentReward = Math.min(engagement.metrics.comments, this.CAPS.COMMENTS) * this.REWARDS.COMMENT;
      const uploadReward = Math.min(engagement.metrics.uploads, this.CAPS.UPLOADS) * this.REWARDS.UPLOAD;
      const upvoteReward = Math.min(engagement.metrics.upvotes_received, this.CAPS.UPVOTES) * this.REWARDS.UPVOTE;

      const totalReward = postReward + commentReward + uploadReward + upvoteReward;

      return RewardDistributionSchema.parse({
        userId,
        totalReward,
        breakdown: {
          postReward,
          commentReward,
          uploadReward,
          upvoteReward,
        }
      });
    } catch (error: any) {
      throw new Error(`Reward calculation failed for ${userId}: ${error.message}`);
    }
  }

  /**
   * Массовый расчет наград для всех активных пользователей эпохи
   */
  async calculateEpochRewards(epoch: number): Promise<any[]> {
    try {
      const usersResponse = await this.axiosInstance.get(`${this.apiBaseUrl}/api/grazer/active_users`, {
        params: { epoch }
      });
      const users = usersResponse.data; // Array of userIds

      const results = [];
      for (const userId of users) {
        try {
          const reward = await this.calculateUserReward(userId, epoch);
          results.push(reward);
        } catch (e) {
          console.error(`Skipping user ${userId}: ${e}`);
        }
      }
      return results;
    } catch (error: any) {
      throw new Error(`Epoch reward calculation failed: ${error.message}`);
    }
  }
}
