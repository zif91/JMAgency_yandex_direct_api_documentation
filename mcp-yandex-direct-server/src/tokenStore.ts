import fs from "fs";
import path from "path";
import crypto from "crypto";

export type StoredToken = {
  createdAt: string;
  login?: string;
  tokenCiphertext?: string; // if encrypted
  tokenPlain?: string; // if not encrypted
};

export class TokenStore {
  private storePath: string;
  private encryptionKey?: Buffer;
  private cache: Record<string, StoredToken> = {};

  constructor(baseDir: string, encryptionKeyBase64?: string) {
    this.storePath = path.join(baseDir, "tokens.json");
    if (encryptionKeyBase64) {
      this.encryptionKey = Buffer.from(encryptionKeyBase64, "base64");
      if (this.encryptionKey.length !== 32) {
        throw new Error("TOKEN_ENCRYPTION_KEY_BASE64 должен быть 32-байтовым ключом (base64)");
      }
    }
    this.load();
  }

  private load() {
    if (fs.existsSync(this.storePath)) {
      const raw = fs.readFileSync(this.storePath, "utf-8");
      try {
        this.cache = JSON.parse(raw);
      } catch {
        this.cache = {};
      }
    }
  }

  private persist() {
    fs.mkdirSync(path.dirname(this.storePath), { recursive: true });
    fs.writeFileSync(this.storePath, JSON.stringify(this.cache, null, 2));
  }

  upsert(secretCode: string, token: string, login?: string) {
    const record: StoredToken = { createdAt: new Date().toISOString(), login };
    if (this.encryptionKey) {
      const iv = crypto.randomBytes(12);
      const cipher = crypto.createCipheriv("aes-256-gcm", this.encryptionKey, iv);
      const ciphertext = Buffer.concat([cipher.update(token, "utf8"), cipher.final()]);
      const tag = cipher.getAuthTag();
      const packed = Buffer.concat([iv, tag, ciphertext]).toString("base64");
      record.tokenCiphertext = packed;
    } else {
      record.tokenPlain = token;
    }
    this.cache[secretCode] = record;
    this.persist();
  }

  resolve(secretCode: string): { token: string; login?: string } | undefined {
    const rec = this.cache[secretCode];
    if (!rec) return undefined;
    if (rec.tokenPlain) return { token: rec.tokenPlain, login: rec.login };
    if (rec.tokenCiphertext && this.encryptionKey) {
      const buf = Buffer.from(rec.tokenCiphertext, "base64");
      const iv = buf.subarray(0, 12);
      const tag = buf.subarray(12, 28);
      const ciphertext = buf.subarray(28);
      const decipher = crypto.createDecipheriv("aes-256-gcm", this.encryptionKey, iv);
      decipher.setAuthTag(tag);
      const token = Buffer.concat([decipher.update(ciphertext), decipher.final()]).toString("utf8");
      return { token, login: rec.login };
    }
    throw new Error("Не удается расшифровать токен: отсутствует ключ шифрования");
  }

  exists(secretCode: string): boolean {
    return secretCode in this.cache;
  }
}