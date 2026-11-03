import React from "react";
import {Search,SlidersHorizontal} from "lucide-react";
export function TransactionFilters({query,onQuery,type,onType}){return <div className="filter-bar"><label className="filter-search"><Search size={16}/><input value={query} onChange={e=>onQuery(e.target.value)} placeholder="Search transactions..."/></label><select className="select-control" value={type} onChange={e=>onType(e.target.value)}><option>All</option><option>Income</option><option>Expenses</option></select><button className="button-secondary"><SlidersHorizontal size={15}/> Filters</button></div>}
}