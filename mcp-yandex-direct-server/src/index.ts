import "dotenv/config";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, CallToolResultSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { OAuthCallbackServer } from "./oauthServer.js";
import { TokenStore } from "./tokenStore.js";
import { YandexDirectClient } from "./yandexClient.js";
import {
  AttachTokenSchema,
  ListAdsSchema,
  ListAdGroupsSchema,
  ListCampaignsSchema,
  ListKeywordsSchema,
  ReportSchema,
  SetActiveTokenSchema,
  StartOAuthSchema,
} from "./types.js";
import { CallServiceSchema } from "./types.js";

const tokenStore = new TokenStore(process.cwd(), process.env.TOKEN_ENCRYPTION_KEY_BASE64);
const activeTokens = new Map<string, { token: string; login?: string }>(); // per secretCode

function getClient(secretCode: string, clientLoginParam?: string): YandexDirectClient {
  const active = activeTokens.get(secretCode) ?? tokenStore.resolve(secretCode);
  if (!active) throw new Error("Не найден активный токен для указанного secretCode");
  const clientLogin = clientLoginParam ?? active.login;
  if (!clientLogin) throw new Error("clientLogin обязателен (не задан ни в вызове, ни в хранилище токена)");
  return new YandexDirectClient({ token: active.token, clientLogin });
}

const server = new Server({ name: "mcp-yandex-direct-server", version: "0.1.0" }, {
  capabilities: {
    tools: {},
  },
});

let oauthServer: OAuthCallbackServer | undefined;

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "start_oauth",
      description: "Запустить OAuth-флоу Яндекс и привязать токен к secretCode. Возвращает ссылку для авторизации.",
      inputSchema: StartOAuthSchema,
    },
    {
      name: "attach_token",
      description: "Привязать уже полученный oauthToken к secretCode (без OAuth-флоу)",
      inputSchema: AttachTokenSchema,
    },
    {
      name: "set_active_token",
      description: "Сделать токен, связанный с secretCode, активным для текущих вызовов",
      inputSchema: SetActiveTokenSchema,
    },
    {
      name: "list_campaigns",
      description: "Получить кампании: параметры SelectionCriteria, FieldNames, Page",
      inputSchema: ListCampaignsSchema,
    },
    {
      name: "list_adgroups",
      description: "Получить группы объявлений",
      inputSchema: ListAdGroupsSchema,
    },
    {
      name: "list_ads",
      description: "Получить объявления",
      inputSchema: ListAdsSchema,
    },
    {
      name: "list_keywords",
      description: "Получить ключевые фразы",
      inputSchema: ListKeywordsSchema,
    },
    {
      name: "get_report",
      description: "Получить отчет (TSV) согласно ReportDefinition из Яндекс.Директ Reports",
      inputSchema: ReportSchema,
    },
    {
      name: "call_service",
      description: "Универсальный вызов сервиса v5: service, method, params",
      inputSchema: CallServiceSchema,
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const name = req.params.name;
  const args = (req.params.arguments ?? {}) as any;

  const ok = (content: any) => ({
    content: [{ type: "text", text: typeof content === "string" ? content : JSON.stringify(content, null, 2) }],
  } satisfies import("@modelcontextprotocol/sdk/types.js").CallToolResult);

  switch (name) {
    case "start_oauth": {
      const { secretCode, scope } = StartOAuthSchema.parse(args);
      const clientId = process.env.YANDEX_CLIENT_ID;
      const clientSecret = process.env.YANDEX_CLIENT_SECRET;
      const redirectUri = process.env.OAUTH_REDIRECT_URI ?? "http://localhost:8787/oauth/callback";
      const port = parseInt(process.env.OAUTH_CALLBACK_PORT ?? "8787", 10);
      if (!clientId || !clientSecret) throw new Error("Не заданы YANDEX_CLIENT_ID / YANDEX_CLIENT_SECRET");

      if (!oauthServer) {
        oauthServer = new OAuthCallbackServer({
          port,
          clientId,
          clientSecret,
          redirectUri,
          onToken: (token) => {
            // Привязываем токен к secretCode (login можно будет указать отдельно при вызовах)
            tokenStore.upsert(secretCode, token);
            activeTokens.set(secretCode, { token });
          },
        });
        oauthServer.start();
      }

      const authUrl = new URL("https://oauth.yandex.ru/authorize");
      authUrl.searchParams.set("response_type", "code");
      authUrl.searchParams.set("client_id", clientId);
      authUrl.searchParams.set("redirect_uri", redirectUri);
      authUrl.searchParams.set("scope", scope);
      return ok({ authorizeUrl: authUrl.toString(), note: "Откройте ссылку, авторизуйтесь и дождитесь подтверждения." });
    }

    case "attach_token": {
      const { secretCode, oauthToken, login } = AttachTokenSchema.parse(args);
      tokenStore.upsert(secretCode, oauthToken, login);
      activeTokens.set(secretCode, { token: oauthToken, login });
      return ok({ attached: true, login: login ?? null });
    }

    case "set_active_token": {
      const { secretCode } = SetActiveTokenSchema.parse(args);
      const resolved = tokenStore.resolve(secretCode);
      if (!resolved) throw new Error("Токен по secretCode не найден");
      activeTokens.set(secretCode, resolved);
      return ok({ active: true });
    }

    case "list_campaigns": {
      const { clientLogin, selectionCriteria, fieldNames, page } = ListCampaignsSchema.parse(args);
      const secretCode = (args.secretCode as string) ?? "default"; // допускаем внешнее управление
      const client = getClient(secretCode, clientLogin);
      const result = await client.callService<any>("campaigns", "get", {
        SelectionCriteria: selectionCriteria,
        FieldNames: fieldNames,
        Page: page,
      });
      return ok(result);
    }

    case "list_adgroups": {
      const { clientLogin, selectionCriteria, fieldNames, page } = ListAdGroupsSchema.parse(args);
      const secretCode = (args.secretCode as string) ?? "default";
      const client = getClient(secretCode, clientLogin);
      const result = await client.callService<any>("adgroups", "get", {
        SelectionCriteria: selectionCriteria,
        FieldNames: fieldNames,
        Page: page,
      });
      return ok(result);
    }

    case "list_ads": {
      const { clientLogin, selectionCriteria, fieldNames, page } = ListAdsSchema.parse(args);
      const secretCode = (args.secretCode as string) ?? "default";
      const client = getClient(secretCode, clientLogin);
      const result = await client.callService<any>("ads", "get", {
        SelectionCriteria: selectionCriteria,
        FieldNames: fieldNames,
        Page: page,
      });
      return ok(result);
    }

    case "list_keywords": {
      const { clientLogin, selectionCriteria, fieldNames, page } = ListKeywordsSchema.parse(args);
      const secretCode = (args.secretCode as string) ?? "default";
      const client = getClient(secretCode, clientLogin);
      const result = await client.callService<any>("keywords", "get", {
        SelectionCriteria: selectionCriteria,
        FieldNames: fieldNames,
        Page: page,
      });
      return ok(result);
    }

    case "get_report": {
      const { clientLogin, reportDefinition, returnMoneyInMicros, maxRetries } = ReportSchema.parse(args);
      const secretCode = (args.secretCode as string) ?? "default";
      const client = getClient(secretCode, clientLogin);
      const tsv = await client.getReport(reportDefinition, { returnMoneyInMicros, maxRetries });
      return ok(tsv);
    }

    case "call_service": {
      const { clientLogin, service, method, params } = CallServiceSchema.parse(args);
      const secretCode = (args.secretCode as string) ?? "default";
      const client = getClient(secretCode, clientLogin);
      const result = await client.callService<any>(service, method, params);
      return ok(result);
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);