import React from "react";
export function BudgetProgress({value,color="#8998ff"}){return <div className="progress-track budget-progress"><i style={{width:`${value}%`,background:color}}/></div>}
}