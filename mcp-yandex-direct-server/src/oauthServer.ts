import express from "express";
import axios from "axios";

export type OAuthServerOptions = {
  port: number;
  clientId: string;
  clientSecret: string;
  redirectUri: string;
  onToken: (token: string, meta?: any) => void;
};

export class OAuthCallbackServer {
  private app = express();
  private server?: any;
  private opts: OAuthServerOptions;

  constructor(opts: OAuthServerOptions) {
    this.opts = opts;
    const callbackPath = safePathFromUrl(opts.redirectUri) ?? "/oauth/callback";
    this.app.get(callbackPath, async (req, res) => {
      const code = req.query["code"] as string | undefined;
      const error = req.query["error"] as string | undefined;
      if (error) {
        res.status(400).send(`OAuth error: ${error}`);
        return;
      }
      if (!code) {
        res.status(400).send("Missing code");
        return;
      }
      try {
        // Яндекс OAuth: обмен кода на токен
        // Документация: https://yandex.ru/dev/id/doc/ru/codes
        const tokenResp = await axios.post(
          "https://oauth.yandex.ru/token",
          new URLSearchParams({
            grant_type: "authorization_code",
            code,
            client_id: this.opts.clientId,
            client_secret: this.opts.clientSecret,
            redirect_uri: this.opts.redirectUri,
          }).toString(),
          { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
        );
        const token = tokenResp.data?.access_token as string;
        this.opts.onToken(token, tokenResp.data);
        res.send("Готово. Можете вернуться в MCP-клиент.");
      } catch (e: any) {
        res.status(500).send(`Не удалось обменять код: ${e?.message}`);
      }
    });
  }

  start() {
    if (this.server) return;
    this.server = this.app.listen(this.opts.port);
  }

  stop() {
    if (this.server) this.server.close();
    this.server = undefined;
  }
}

function safePathFromUrl(urlStr: string): string | undefined {
  try {
    const u = new URL(urlStr);
    return u.pathname || "/oauth/callback";
  } catch {
    return undefined;
  }
}