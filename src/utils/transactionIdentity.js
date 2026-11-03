
const normalizeText = (value = "") =>
  String(value)
    .normalize("NFKC")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");

const normalizeAmount = (value) => {
  const amount = Number(
    String(value ?? "").replace(/,/g, "").trim()
  );

  if (!Number.isFinite(amount) || amount < 0) {
    throw new TypeError("Invalid transaction amount");
  }

  return amount.toFixed(2);
};

const normalizeTimestamp = (value) => {
  const date = new Date(value);
  const timestamp = date.getTime();

  if (!Number.isFinite(timestamp)) {
    throw new TypeError("Invalid transaction timestamp");
  }

  // Group equivalent capture events into 30-second windows.
  return Math.floor(timestamp / 30_000);
};

export function getTransactionFingerprint(transaction) {
  if (!transaction || typeof transaction !== "object") {
    throw new TypeError("Transaction must be an object");
  }

  const reference = normalizeText(
    transaction.referenceId || transaction.transactionId || ""
  );

  const merchant = normalizeText(
    transaction.merchant || transaction.counterparty || "unknown"
  );

  const amount = normalizeAmount(transaction.amount);

  const currency = normalizeText(
    transaction.currency || "unknown"
  );

  const type = normalizeText(
    transaction.type || "debit"
  );

  const source = normalizeText(
    transaction.source || transaction.app || "manual"
  );

  // A real payment reference is stronger than heuristic matching.
  if (reference) {
    return `ref:${source}:${reference}`;
  }

  const timestamp = normalizeTimestamp(
    transaction.timestamp || transaction.date
  );

  return [
    "txn",
    source,
    merchant,
    amount,
    currency,
    type,
    timestamp
  ].join(":");
}
