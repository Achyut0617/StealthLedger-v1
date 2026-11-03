import React from "react";
import {transactions} from "../../data";
import {ShoppingBag,Car,Play, Coffee,ArrowDownLeft} from "lucide-react";
const icons={shopping:ShoppingBag,car:Car,play:Play,coffee:Coffee,income:ArrowDownLeft};
export function RecentTransactions(){return <div className="table-scroll"><table className="data-table"><thead><tr><th>TRANSACTION</th><th>CATEGORY</th><th>DATE</th><th>PAYMENT METHOD</th><th className="align-right">AMOUNT</th></tr></thead><tbody>{transactions.slice(0,5).map(t=>{const Icon=icons[t.icon]||ShoppingBag;return <tr key={t.id}><td><div className="transaction-name"><span className={`transaction-icon ${t.amount>0?"income-bg":""}`}><Icon size={16}/></span><b>{t.name}</b></div></td><td>{t.category}</td><td>{t.date}</td><td>{t.method}</td><td className={`amount ${t.amount>0?"positive":"negative"}`}>{t.amount>0?"+":"−"}${Math.abs(t.amount).toFixed(2)}</td></tr>})}</tbody></table></div>}
}