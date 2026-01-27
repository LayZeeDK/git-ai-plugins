#!/usr/bin/env node
// Output current UTC timestamp in YYYYMMDD-HHmmssZ format
const now = new Date();
const pad = (n) => String(n).padStart(2, '0');

const year = now.getUTCFullYear();
const month = pad(now.getUTCMonth() + 1);
const day = pad(now.getUTCDate());
const hours = pad(now.getUTCHours());
const minutes = pad(now.getUTCMinutes());
const seconds = pad(now.getUTCSeconds());

console.log(`${year}${month}${day}-${hours}${minutes}${seconds}Z`);
