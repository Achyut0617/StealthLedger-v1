import React from "react";
import {ShoppingBag,Car,Play,Coffee,ArrowDownLeft,MoreHorizontal} from "lucide-react";
const icons={shopping:ShoppingBag,car:Car,play:Play,coffee:Coffee,income:ArrowDownLeft};
export function TransactionCard({transaction:t}){const Icon=icons[t.icon]||ShoppingBag;return <div className="transaction-card"><span className={`transaction-icon ${t.amount>0?"income-bg":""}`}><Icon size={17}/></span><div className="transaction-card-main"><b>{t.name}</b><small>{t.category} · {t.date}</small></div><div className={`amount ${t.amount>0?"positive":"negative"}`}>{t.amount>0?"+":"−"}${Math.abs(t.amount).toFixed(2)}</div><button className="icon-button"><MoreHorizontal size={18}/></button></div>}
}