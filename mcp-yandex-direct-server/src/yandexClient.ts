import axios, { AxiosInstance } from "axios";

export type YandexClientOptions = {
  baseUrl?: string;
  token: string;
  clientLogin: string;
};

export class YandexDirectClient {
  private http: AxiosInstance;
  private clientLogin: string;

  constructor(opts: YandexClientOptions) {
    const baseUrl = opts.baseUrl ?? "https://api.direct.yandex.com/json/v5";
    this.clientLogin = opts.clientLogin;
    this.http = axios.create({
      baseURL: baseUrl,
      headers: {
        Authorization: `Bearer ${opts.token}`,
        "Client-Login": this.clientLogin,
        "Accept-Language": "ru",
        "Content-Type": "application/json; charset=utf-8",
      },
      timeout: 60000,
      validateStatus: () => true,
    });
  }

  async callService<T>(service: string, method: string, params: Record<string, unknown>): Promise<T> {
    const url = `/${service}`;
    const body = { method, params };
    const resp = await this.http.post(url, body);
    if (resp.status !== 200) {
      throw new Error(`HTTP ${resp.status}: ${JSON.stringify(resp.data)}`);
    }
    if (resp.data.error) {
      throw new Error(`API error: ${JSON.stringify(resp.data.error)}`);
    }
    return resp.data.result as T;
  }

  async getReport(reportDefinition: Record<string, unknown>, options?: { returnMoneyInMicros?: boolean; maxRetries?: number }): Promise<string> {
    const url = `/reports`;
    const maxRetries = options?.maxRetries ?? 5;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      const resp = await this.http.post(url, { params: reportDefinition }, {
        headers: {
          returnMoneyInMicros: String(options?.returnMoneyInMicros ?? false),
        },
        responseType: "text",
      });
      if (resp.status === 200) {
        return resp.data as string; // TSV
      }
      if (resp.status === 201 || resp.status === 202) {
        const retryInHeader = resp.headers["retryin"] ?? resp.headers["retryIn"];
        const retryIn = parseInt(Array.isArray(retryInHeader) ? retryInHeader[0] : (retryInHeader ?? "30"), 10) || 30;
        await new Promise((r) => setTimeout(r, retryIn * 1000));
        continue;
      }
      if (resp.status >= 400 && resp.status < 500) {
        throw new Error(`Report client error ${resp.status}: ${resp.data}`);
      }
      // 5xx retry with backoff
      await new Promise((r) => setTimeout(r, Math.min(60000, 1000 * (attempt + 1) ** 2)));
    }
    throw new Error("Не удалось получить отчет после нескольких попыток");
  }
}