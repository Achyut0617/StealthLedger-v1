import React,{useState} from "react";
import {Sidebar} from "./Sidebar";
import {Topbar} from "./Topbar";
import {MobileNavigation} from "./MobileNavigation";
export function AppShell({activePage,onNavigate,children}){
 const [mobileOpen,setMobileOpen]=useState(false);
 return <div className="app-shell"><Sidebar activePage={activePage} onNavigate={onNavigate}/><main className="main-area"><Topbar title={activePage} onMenu={()=>setMobileOpen(!mobileOpen)}/><div className="page-content">{children}</div></main>{mobileOpen&&<MobileNavigation activePage={activePage} onNavigate={p=>{onNavigate(p);setMobileOpen(false)}} onClose={()=>setMobileOpen(false)}/>}</div>;
}