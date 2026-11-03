import React from "react";
import {BudgetProgress} from "./BudgetProgress";
import {MoreHorizontal} from "lucide-react";
export function BudgetCard({budget:b}){const pct=Math.min(100,b.spent/b.limit*100);return <article className="panel budget-card"><div className="budget-card-head"><div className="budget-dot" style={{background:b.color}}/><b>{b.name}</b><button className="icon-button"><MoreHorizontal size={17}/></button></div><h2>${b.spent}<small> / ${b.limit}</small></h2><BudgetProgress value={pct} color={b.color}/><div className="budget-foot"><span>{Math.round(pct)}% used</span><b>${b.limit-b.spent} left</b></div></article>}
}