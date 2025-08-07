import { z } from "zod";

export const WithClientLoginSchema = z.object({
  clientLogin: z.string().min(1, "clientLogin обязателен"),
});

export const WithSecretSchema = z.object({
  secretCode: z.string().min(6, "secretCode должен быть не короче 6 символов"),
});

export const AttachTokenSchema = WithSecretSchema.extend({
  oauthToken: z.string().min(10, "Неверный oauthToken"),
  login: z.string().optional(),
});

export const StartOAuthSchema = WithSecretSchema.extend({
  scope: z.string().default("direct:api"),
});

export const SetActiveTokenSchema = WithSecretSchema;

export const ListCampaignsSchema = WithClientLoginSchema.extend({
  selectionCriteria: z.record(z.any()).default({}),
  fieldNames: z.array(z.string()).default(["Id", "Name", "Status"]),
  page: z.object({ Limit: z.number().int().positive().max(10000).default(1000), Offset: z.number().int().nonnegative().default(0) }).default({ Limit: 1000, Offset: 0 }),
});

export const ListAdGroupsSchema = WithClientLoginSchema.extend({
  selectionCriteria: z.record(z.any()).default({}),
  fieldNames: z.array(z.string()).default(["Id", "Name", "CampaignId", "Status"]),
  page: z.object({ Limit: z.number().int().positive().max(10000).default(1000), Offset: z.number().int().nonnegative().default(0) }).default({ Limit: 1000, Offset: 0 }),
});

export const ListAdsSchema = WithClientLoginSchema.extend({
  selectionCriteria: z.record(z.any()).default({}),
  fieldNames: z.array(z.string()).default(["Id", "AdGroupId", "CampaignId", "Status"]),
  page: z.object({ Limit: z.number().int().positive().max(10000).default(1000), Offset: z.number().int().nonnegative().default(0) }).default({ Limit: 1000, Offset: 0 }),
});

export const ListKeywordsSchema = WithClientLoginSchema.extend({
  selectionCriteria: z.record(z.any()).default({}),
  fieldNames: z.array(z.string()).default(["Id", "AdGroupId", "CampaignId", "State", "Keyword"]),
  page: z.object({ Limit: z.number().int().positive().max(10000).default(1000), Offset: z.number().int().nonnegative().default(0) }).default({ Limit: 1000, Offset: 0 }),
});

export const ReportSchema = WithClientLoginSchema.extend({
  reportDefinition: z.object({}).passthrough(),
  returnMoneyInMicros: z.boolean().default(false),
  maxRetries: z.number().int().positive().max(20).default(5),
});

export const CallServiceSchema = z.object({
  secretCode: z.string().optional(),
  clientLogin: z.string().min(1),
  service: z.string().min(1),
  method: z.enum(["add", "get", "update", "delete", "suspend", "resume"]).or(z.string()),
  params: z.object({}).passthrough(),
});

export type WithClientLogin = z.infer<typeof WithClientLoginSchema>;
export type WithSecret = z.infer<typeof WithSecretSchema>;
export type AttachTokenInput = z.infer<typeof AttachTokenSchema>;
export type StartOAuthInput = z.infer<typeof StartOAuthSchema>;
export type SetActiveTokenInput = z.infer<typeof SetActiveTokenSchema>;
export type ListCampaignsInput = z.infer<typeof ListCampaignsSchema>;
export type ListAdGroupsInput = z.infer<typeof ListAdGroupsSchema>;
export type ListAdsInput = z.infer<typeof ListAdsSchema>;
export type ListKeywordsInput = z.infer<typeof ListKeywordsSchema>;
export type ReportInput = z.infer<typeof ReportSchema>;
export type CallServiceInput = z.infer<typeof CallServiceSchema>;