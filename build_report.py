"""Generate the five-page academic technical summary from outputs/simulation_summary.json."""
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/"outputs"/"simulation_summary.json").read_text())
sc=data["scenarios"]; im=data["initial_margin_policy"]; mp=data["mpor_policy"]; cfg=data["configuration"]
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name="Cover",parent=styles["Title"],fontSize=24,leading=29,textColor=colors.HexColor("#17324D"),spaceAfter=10))
styles.add(ParagraphStyle(name="H1x",parent=styles["Heading1"],fontSize=16,textColor=colors.HexColor("#17324D"),spaceAfter=8))
styles.add(ParagraphStyle(name="H2x",parent=styles["Heading2"],fontSize=11,textColor=colors.HexColor("#2E6F95"),spaceBefore=6,spaceAfter=4))
styles.add(ParagraphStyle(name="Bodyx",parent=styles["BodyText"],fontSize=8.5,leading=12,spaceAfter=5))
styles.add(ParagraphStyle(name="Smallx",parent=styles["BodyText"],fontSize=7,textColor=colors.HexColor("#5D6B75")))
P=lambda t,s="Bodyx":Paragraph(t,styles[s])
def table(rows,widths,font=7):
    t=Table(rows,colWidths=widths,repeatRows=1)
    cmd=[("BACKGROUND",(0,0),(-1,0),colors.HexColor("#17324D")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),font),("GRID",(0,0),(-1,-1),.25,colors.HexColor("#D6E0E7")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]
    for i in range(2,len(rows),2):cmd.append(("BACKGROUND",(0,i),(-1,i),colors.HexColor("#F1F5F8")))
    t.setStyle(TableStyle(cmd));return t
story=[]
# 1 executive
story += [P("QUANTITATIVE RISK MANAGEMENT · COLLABORATIVE UNIVERSITY RESEARCH","Smallx"),P("OTC Derivatives Margining &amp; Systemic Liquidity Risk","Cover"),P("Five-page technical summary · corrected stylized Monte Carlo implementation"),P("Executive summary","H1x"),P("This project studies the trade-off between counterparty protection and investor liquidity in a stylized non-centrally-cleared OTC forward. Institution A is long the forward, holds limited cash and illiquid assets, and may default from an exogenous shock or an unmet margin call. Institution B is the solvent dealer. The model examines initial margin (IM), variation margin (VM), close-out during the margin period of risk (MPOR), fire sales and systemic liquidity feedback."),P("The corrected run uses 20,000 paths, 252 observation days, a 10-day MPOR and maturity parameter 300 days. It separates the observation window from the additional MPOR close-out segment and corrects collateral-settlement and fire-sale accounting."),table([["Key metric","Result"],["99% initial margin",f"${cfg['initial_margin_99pct']:,.2f}"],["Investor default · fire-sale setup",f"{sc['fire_sale_daily_vm']['default_rate']:.2%}"],["Paths with fire sales",f"{sc['fire_sale_daily_vm']['fire_sale_path_rate']:.2%}"],["Mean fire-sale cost per path",f"${sc['fire_sale_daily_vm']['mean_fire_sale_cost_per_path']:,.2f}"]],[85*mm,85*mm]),P("The results are stylized outputs, not empirical default forecasts, regulatory estimates or investment advice.","Smallx"),PageBreak()]
# 2 derivation
story += [P("1. Contract and initial margin","H1x"),P("A is long a forward with value V_t = Q(S_t − K). The asset follows arithmetic Brownian motion with zero drift: ΔS = σ_s√Δt Z, Z ~ N(0,1). Dollar volatility is σ_s = annualized volatility × S_0. With S_0 = K = $100, Q = 1,000 and 20% volatility, σ_s = $20 per square-root year."),P("The one-sided 99% delta-normal IM over MPOR is:"),P("IM = z_0.99 × Q × σ_s × √(MPOR/252), with z_0.99 = 2.3263479."),table([["Parameter","Baseline"],["S0 / K","$100 / $100"],["Position Q","1,000"],["Annual volatility","20%"],["Annual exogenous PD","1%"],["MPOR","10 trading days"],["Initial cash L0","$20,000"],["Illiquid assets A0","$15,000"],["Fire-sale discount","10%"]],[85*mm,85*mm]),P("The annual default probability is converted to intensity λ = −ln(1−PD), with daily probability 1−exp(−λ/252). The geometric default-time draw calibrates the one-year cumulative default probability to the selected annual PD."),PageBreak()]
# 3 liquidity
base=sc["unlimited_cash_daily_vm"]; fs=sc["fire_sale_daily_vm"]; wk=sc["weekly_vm"]; el=sc["eligible_illiquid_vm_collateral"]
story += [P("2. Liquidity stress and dealer loss","H1x"),table([["Metric","Unlimited cash","Fire-sale liquidity"],["Investor default",f"{base['default_rate']:.2%}",f"{fs['default_rate']:.2%}"],["Liquidity default",f"{base['liquidity_default_rate']:.2%}",f"{fs['liquidity_default_rate']:.2%}"],["Paths with fire sales",f"{base['fire_sale_path_rate']:.2%}",f"{fs['fire_sale_path_rate']:.2%}"],["Fire-sale cost / path",f"${base['mean_fire_sale_cost_per_path']:,.2f}",f"${fs['mean_fire_sale_cost_per_path']:,.2f}"],["Mean dealer loss / path",f"${base['mean_dealer_loss']:,.2f}",f"${fs['mean_dealer_loss']:,.2f}"],["P(loss > 0)",f"{base['probability_positive_loss']:.2%}",f"{fs['probability_positive_loss']:.2%}"],["Conditional P99 dealer loss",f"${base['conditional_p99']:,.0f}",f"${fs['conditional_p99']:,.0f}"]],[58*mm,56*mm,56*mm],font=6.7),P("The unlimited-cash case isolates exogenous default. With limited cash, adverse VM calls can force discounted asset sales. Dealer close-out loss is calculated from the close-out MTM less IM actually held and the last successfully settled VM balance. The default-day unpaid call is not treated as collateral."),P("Conditional loss percentiles are calculated only among paths with positive dealer losses; the unconditional distribution has a point mass at zero."),PageBreak()]
# 4 policy
rows=[["IM multiplier","IM","Investor default","Fire-sale cost/path","Conditional P99 loss"]]
for r in im:rows.append([f"{r['IM multiplier']:.1f}",f"${r['IM ($)']:,.0f}",f"{r['Default rate']:.2%}",f"${r['Fire-sale cost/path']:,.0f}",f"${r['Conditional dealer P99 loss']:,.0f}"])
story += [P("3. Policy experiments","H1x"),P("Higher IM protects the dealer by increasing collateral but consumes investor liquidity and raises liquidity-driven default and fire-sale costs."),table(rows,[28*mm,32*mm,32*mm,38*mm,40*mm],font=6.4),P("Weekly VM versus daily VM","H2x"),table([["Metric","Daily","Weekly (5-day)"],["Investor default",f"{fs['default_rate']:.2%}",f"{wk['default_rate']:.2%}"],["Fire-sale cost/path",f"${fs['mean_fire_sale_cost_per_path']:,.2f}",f"${wk['mean_fire_sale_cost_per_path']:,.2f}"],["Mean dealer loss/path",f"${fs['mean_dealer_loss']:,.2f}",f"${wk['mean_dealer_loss']:,.2f}"]],[60*mm,60*mm,60*mm]),P("MPOR sensitivity","H2x"),table([["MPOR","IM","Investor default","Fire-sale cost/path"],*[ [f"{r['MPOR (days)']} days",f"${r['IM ($)']:,.0f}",f"{r['Default rate']:.2%}",f"${r['Fire-sale cost/path']:,.2f}"] for r in mp]],[35*mm,45*mm,45*mm,55*mm]),P("Shorter MPOR reduces IM and investor liquidity pressure but changes the dealer's uncollateralized close-out window. The trade-off must be evaluated across both parties' risk measures."),PageBreak()]
# 5 systemic limitations
fixed=sc["procyclical_fixed_15pct_IM"]; dyn=sc["procyclical_dynamic_IM"]; sys=sc["systemic_haircut"]
story += [P("4. Procyclical margins, systemic feedback and limitations","H1x"),P("The dynamic IM experiment switches annualized volatility between 15% and 30% following a daily decline greater than 2% of S0. IM is recalculated and excess IM is released when required margin declines."),table([["Metric","Fixed 15% IM","Dynamic 15% / 30% IM"],["Investor default",f"{fixed['default_rate']:.2%}",f"{dyn['default_rate']:.2%}"],["Liquidity default",f"{fixed['liquidity_default_rate']:.2%}",f"{dyn['liquidity_default_rate']:.2%}"],["Fire-sale cost/path",f"${fixed['mean_fire_sale_cost_per_path']:,.2f}",f"${dyn['mean_fire_sale_cost_per_path']:,.2f}"],["Mean dealer loss",f"${fixed['mean_dealer_loss']:,.2f}",f"${dyn['mean_dealer_loss']:,.2f}"]],[60*mm,60*mm,60*mm]),P(f"The systemic extension links the haircut to the previous day's share of investors selling assets. The recorded mean haircut is {sys['mean_systemic_haircut']:.2%}; maximum is {sys['max_systemic_haircut']:.2%}. The model does not include correlated defaults or common asset returns."),P("Corrections and limitations","H2x"),P("Corrections include: 252-day observation window with an MPOR close-out extension; last successfully settled VM balance; no default-day VM; full close-out horizon; fire-sale cost only on assets sold; initial IM shortfall funding; weekly VM accumulation; and release of excess procyclical IM."),P("Limitations include arithmetic-Brownian prices, an always-solvent dealer, independent exogenous defaults, fixed collateral value, simplified settlement and no cross-investor default correlation. Outcomes depend on parameters and random seeds and are not validated regulatory forecasts."),P("Collaborative university project. Public copy omits student identifiers and group roster. No external market data are included. No open-source licence is granted.","Smallx")]

def footer(canvas,doc):
    canvas.saveState();w,h=A4
    canvas.setStrokeColor(colors.HexColor("#D6E0E7"));canvas.line(20*mm,14*mm,w-20*mm,14*mm)
    canvas.setFont("Helvetica",7);canvas.setFillColor(colors.HexColor("#596b7c"))
    canvas.drawString(20*mm,9*mm,"OTC DERIVATIVES MARGINING · TECHNICAL SUMMARY")
    canvas.drawRightString(w-20*mm,9*mm,f"{doc.page} / 5")
    canvas.restoreState()

out=ROOT/"docs"/"OTC_Margining_Technical_Summary.pdf"
SimpleDocTemplate(str(out),pagesize=A4,rightMargin=20*mm,leftMargin=20*mm,topMargin=15*mm,bottomMargin=20*mm,title="OTC Derivatives Margining Technical Summary").build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
