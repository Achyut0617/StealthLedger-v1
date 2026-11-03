import React from "react";
export function TransactionDetails({transaction}){if(!transaction)return null;return <div className="panel"><div className="eyebrow">TRANSACTION DETAILS</div><h2>{transaction.name}</h2><h1 className="detail-amount">${Math.abs(transaction.amount).toFixed(2)}</h1><p>{transaction.category} · {transaction.date}</p><p className="muted-text">{transaction.method}</p></div>}
}