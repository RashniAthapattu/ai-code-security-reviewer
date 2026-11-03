import type { Language } from "./types";

// Short, deliberately insecure snippets for the "Try an example" button.
export const EXAMPLES: Record<Language, string> = {
  python: `import hashlib
import pickle
import subprocess

API_PASSWORD = "hunter2"


def list_files(path):
    return subprocess.call("ls " + path, shell=True)


def checksum(data):
    return hashlib.md5(data).hexdigest()


def load_session(blob):
    return pickle.loads(blob)


def calculate(expression):
    return eval(expression)
`,
  javascript: `const crypto = require("crypto");
const child_process = require("child_process");

const apiKey = "sk_live_51H8exampleexample";

function showGreeting(name) {
  document.getElementById("greeting").innerHTML = "Hello " + name;
}

function runReport(filename) {
  child_process.exec("cat " + filename);
}

function findUser(db, id) {
  return db.query("SELECT * FROM users WHERE id = " + id);
}

function calculate(expression) {
  return eval(expression);
}

function checksum(text) {
  return crypto.createHash("md5").update(text).digest("hex");
}
`,
  typescript: `import { exec } from "child_process";

const apiKey: string = "sk_live_51H8exampleexample";

export function showGreeting(name: string): void {
  document.getElementById("greeting")!.innerHTML = "Hello " + name;
}

export function runReport(filename: string): void {
  exec("cat " + filename);
}

export function calculate(expression: string): unknown {
  return eval(expression);
}
`,
};

export const MAX_CODE_LENGTH = 100_000; // same limit as the backend
