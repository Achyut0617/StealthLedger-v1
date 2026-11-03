import React, {useState} from "react";
import {AppShell} from "./components/layout/AppShell";
import {DashboardOverview} from "./components/dashboard/DashboardOverview";
import {TransactionList} from "./components/transactions/TransactionList";
import {BudgetOverview} from "./components/budgets/BudgetOverview";
import {PrivacySettings} from "./components/settings/PrivacySettings";
export default function App(){
 const [page,setPage]=useState("Overview");
 const render=()=> page==="Transactions" ? <TransactionList/> : page==="Budgets" ? <BudgetOverview/> : page==="Settings" ? <PrivacySettings/> : <DashboardOverview/>;
 return <AppShell activePage={page} onNavigate={setPage}>{render()}</AppShell>;
}