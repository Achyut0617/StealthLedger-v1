import React from "react";
import {ShoppingBasket,Car,Utensils,Monitor,Heart} from "lucide-react";
const items=[["Groceries",420,26,ShoppingBasket,"#8998ff"],["Transport",168,17,Car,"#42c6a5"],["Dining out",285,22,Utensils,"#f4ad66"],["Subscriptions",48,12,Monitor,"#c28bf3"],["Health",92,9,Heart,"#e879a5"]];
export function CategoryBreakdown(){return <div className="category-list">{items.map(([name,amount,percent,Icon,color])=><div className="category-row" key={name}><div className="category-icon" style={{color,background:`${color}18`}}><Icon size={16}/></div><div className="category-info"><div><b>{name}</b><span>${amount}</span></div><div className="progress-track"><i style={{width:`${percent*3}%`,background:color}}/></div></div></div>)}</div>}
}