## Seek and Trade — Seeker (orchestrateur multi‑stratégies, IBKR, 1 000 $)

### Objectif
Un seul bot, nommé Seeker, orchestre plusieurs stratégies d’options risk‑defined et s’adapte au régime de marché, aux événements et à la liquidité. Aucune valeur de repli en exécution: si une donnée essentielle manque, le bot n’ouvre pas de trade.

### Portée (v1)
- Compte non enregistré, capital de référence: 1 000 $
- DTE d’entrée cible ≈ 45 (plage 35–55), gestion vers 21 DTE
- Exécution Interactive Brokers (TWS/IB Gateway) via API (ib_insync)
- Heures RTH uniquement; USD/CAD gérées automatiquement (IDEALPRO) sous contrôles stricts

---

### Stratégies (5) — risk‑defined et compatibles petit capital
1) Credit Spreads (bull/bear)
   - Entrée: short ≈ delta 0,10–0,15; aile à 0,50 $ ou 1,00 $ plus loin; DTE ~45
   - Gestion: TP +50% du crédit; stop 1,5–2,0× crédit OU delta short > 0,30; sortie si non résolu à 21 DTE

2) Iron Condor
   - Entrée: jambes courtes ≈ delta 0,10–0,15 de part et d’autre; ailes 0,50–1,00 $; DTE ~45
   - Gestion: TP +40–50%; sortie anticipée si sous‑jacent touche une jambe courte; gérer à 21 DTE

3) Diagonale / Calendrier
   - Entrée: long 60–90 DTE (faible theta), short 21–30 DTE (theta élevé), strike légèrement OTM
   - Gestion: rachat short à +50–60% ou 7–10 DTE; rouler; stop si P/L global < seuil risque

4) Iron Fly (ailes étroites)
   - Entrée: vendre straddle central, acheter ailes 0,50–1,00 $; cible vol élevée et range serré
   - Gestion: TP +40–50%; surveiller gamma; éviter proche d’événements majeurs

5) Broken‑Wing Butterfly (crédit)
   - Entrée: asymétrique pour capter le skew IV; risque net plafonné, coût souvent bas
   - Gestion: TP +40–50%; stop si déplacement rapide vers l’aile courte défavorable

Sélection (règles v1):
- Range + IVR élevé → Iron Condor ou Iron Fly
- Tendance + IVR élevé → Credit Spread côté tendance
- IVR bas → Diagonale/Calendrier
- Skew marqué → Broken‑Wing Butterfly
- Événements (earnings/macro J‑1): éviter l’ouverture, ou réduire la taille; privilégier ETF

---

### Agents (internes) et orchestration
- Risk Guard (veto dur): budget/répartition du risque, plafonds par secteur/cluster, par sous‑jacent
- Liquidity/Slippage: bid/ask, OI/volume, stabilité; refuse si coûts > seuils
- Regime Classifier: IV Rank/Percentile, tendance (SMA 20/50, ADX), structure de terme, range/breakout
- Event Risk: macro (CPI/FOMC/NFP), earnings, jours fériés; applique évitement/réduction
- Strategy Generator: propose 1–3 setups calibrés (DTE, delta, largeur)
- Critic/Stress: stress tests (gap, spike IV, touch jambe courte), pénalise les setups fragiles
- FX Router: choix USD/CAD selon EV net (commissions + FX), conversions IDEALPRO
- Execution: ordres multi‑jambes limit, TP/SL, gestion à 21 DTE, RTH uniquement
- Post‑Trade Analyst: journalisation, attribution, métriques par régime/stratégie

Pipeline décisionnel (propose → critique → veto → exécution):
- Generator → Critic → Risk/Liquidity/Event/FX (veto dur) → Execute
- En cas de désaccord ou de données manquantes: pas de trade (erreur explicite)

---

### Limites de risque initiales (obligatoires, à configurer)
- Risque max par trade: ≤ 10% du capital (≤ 100 $)
- Risque total engagé: ≤ 25% du capital
- Plafond par secteur (GICS/ETF proxy): ≤ 40% du risque total
- Plafond par cluster de corrélation (rolling 60 j): ≤ 50% du risque total
- Plafond par sous‑jacent: ≤ 15% du risque total

Remarque exécution: ces valeurs doivent être définies explicitement dans la configuration runtime. Si manquantes, le bot stoppe (aucun défaut implicite).

---

### Seuils initialement recommandés (liquidité, événements, FX)
- Liquidité:
  - Bid/Ask par jambe: ≤ 0,05 $
  - Open Interest par strike: ≥ 500
  - Volume options quotidien par chaîne: ≥ 1 000
  - Strikes serrés (increments 0,50 $ / 1,00 $)
- Événements:
  - Macro majeurs (CPI/FOMC/NFP): pas d’ouverture ≤ J‑1; si position ouverte, réduction/close partielle selon règles
  - Earnings (single‑stock): pas d’ouverture ≤ J‑3; privilégier ETF cette semaine
- FX (USD/CAD):
  - Conversion via IDEALPRO avec slippage max toléré: ≤ 1 pip; au‑delà, annuler
  - Exposition devise suivie; pas d’ordres si conversion requise échoue

Ces seuils sont à fournir dans la config; absence → erreur (no‑trade).

---

### Score de confiance (v1) — simple, dépendant du temps
But: affichage 0–100 reflétant marge de temps (DTE), distance du prix aux strikes, delta de la jambe courte, IVR, risques événementiels et gamma.

Composantes (normalisées 0–1) et pondérations initiales:
- Temps (w_t = 0,35): g(DTE) croît avec DTE, plafonné à 45; plus de confiance en début de vie
- Delta jambe courte (w_Δ = 0,20): décroît si delta → 0,30
- Distance prix/strike vs ATR (w_dist = 0,15): plus la distance en multiples d’ATR est grande, mieux c’est
- IV Rank (w_IVR = 0,10): favorable si la stratégie est alignée au régime IVR
- Theta capture/PnL réalisé (w_PnL = 0,10): bonus si décote déjà capturée
- Événements (w_evt = 0,10): pénalité si événement proche

Score = clamp(0..100)[ 100 × (w_t·g(DTE) + w_Δ·fΔ + w_dist·fdist + w_IVR·fIVR + w_PnL·fPnL + w_evt·fevt − w_γ·fgamma) ], avec w_γ inclus dans fevt/fin de vie.

Affichage UI: jauge + badges “rassure”/“inquiète” (ex.: Δ 0,12, Dist 1,8×ATR, IVR 68, CPI J‑1, Gamma ↑).

---

### Sélection USD/CAD
- Calcul EV net = (crédit attendu − commissions − coût/risque FX) / risque engagé
- Choix de la place (US vs CA) avec EV net max
- Conversion FX si nécessaire (montant exact + commissions); si cotations/taux indisponibles ou slippage > seuil → pas d’ordre

---

### Interface (dark) — supervision et transparence
- Portefeuille: cartes par position (symbole, stratégie, DTE, largeur, crédit, IVR, régime, secteur, devise)
- Confiance: jauge 0–100 + liste “rassure/inquiète” contextualisée
- Progression DTE: barre 45 → 21 → 0, rappels de gestion
- Détails stratégie: payoff T+0/T+X, greeks, prob. touch, strikes, logs de décision
- Journal global: toutes les décisions, votes/penalités d’agents, coûts, FX, raisons de non‑trade
- Paramètres: seuils durs, plafonds secteur/cluster, règles FX (édition contrôlée)

---

### Journalisation & supervision
- Chaque décision: snapshot features, scores d’agents, contraintes, ordre envoyé (ou refusé) et raison
- Post‑trade: PnL, slippage, MFE/MAE, respect des règles, temps en position, gestion à 21 DTE
- Rapports: par stratégie, par régime, par secteur/cluster, par devise
- Mode “shadow”: tester des alternatives sans exécuter (recherche)

---

### Roadmap
- v1: Règles + 5 stratégies + agents internes + UI minimale + journaux; paper trading IBKR
- v1.1: Optimisation paramétrique simple par régime (grid/BO) hors‑ligne; rapports
- v2: Bandit contextuel pour pondérer la sélection de stratégie sous contraintes “dures”; rollbacks auto
- v3: “Manager” (dashboard avancé, revue, validation humaine), scénarios A/B; agents externalisables si besoin

---

### Tests & sécurité
- Paper d’abord; check‑list d’ordres (validation des legs, taille, limites, RTH)
- Tests unitaires des agents (Risk, Liquidity, Event, FX, Generator, Critic)
- Tests d’intégration IBKR (simulés, puis paper)
- Aucune valeur par défaut silencieuse: config manquante → erreur, pas de trade

---

### Config (exigée, pas de défauts implicites)
À fournir avant exécution (exemple de clés, valeurs à décider explicitement):
- risk.max_per_trade_pct, risk.max_portfolio_pct, risk.max_sector_pct, risk.max_corr_cluster_pct, risk.max_per_underlying_pct
- liquidity.max_leg_spread, liquidity.min_open_interest, liquidity.min_chain_volume
- events.macro_buffer_days, events.earnings_buffer_days
- fx.max_slippage_pips
- strategies.enabled = [credit_spread, iron_condor, diagonal, iron_fly, broken_wing_butterfly]
- bandit.alpha, bandit.feature_dim

---

### Note R&D — approche évolutive (génétique) et agents “parents/enfants”
Utilisation recommandée: hors‑ligne, sur historiques et en mode shadow. On fait évoluer des “policies” (pondérations, seuils souples) sous contraintes “dures” (Risk/Liquidity/Event/FX). Les meilleurs passent en candidates; en live, l’orchestrateur reste déterministe et le bandit contextuel ajuste prudemment. Jamais de prise de décision live purement “évolutive” sans garde‑fous.

---

### Points ouverts (à préciser au fil des itérations)
- Liste initiale des sous‑jacents/ETF éligibles (US/CA) et mapping secteur/cluster
- Source calendrier macro/earnings (fournisseur choisi)
- Poids du score de confiance (ajustements empiriques)
- Seuils par stratégie (affinage après paper)

---

### Démarrage rapide (Docker)
- Construire et lancer:
  - `docker compose build seeker`
  - `docker compose up -d seeker`
- UI: ouvrir `http://localhost:8001/` (thème sombre)
- Arrêter: `docker compose down`

Ports:
- Hôte 8001 → Conteneur 8000 (évite conflit local sur 8000)

Volumes:
- `./config` monté en lecture seule sur `/app/config`
- `./data` monté sur `/app/data` (écritures: decisions.jsonl)

Variables d’environnement:
- `CONFIG_PATH=/app/config/config.json` (déjà défini dans l’image)

---

### API (Seeker)
- `GET /health` → { status, actions, feature_dim }
- `POST /decision` (règle stricte, pas de valeurs de repli):
  - Payload requis:
    - features: float[] de taille = bandit.feature_dim
    - dte: int
    - short_delta, distance_atr, ivr_norm, theta_captured, event_buffer, gamma_risk: float
  - Réponse: { chosen, features, actions, confidence { score, components } }
  - Journalisation: append JSONL dans `/app/data/decisions.jsonl`
- `POST /risk/evaluate`:
  - Payload: { proposed_risk_pct, portfolio_risk_pct, sector_risk_pct, corr_cluster_risk_pct, underlying_risk_pct }
  - Réponse: { allowed: bool, reason: string }
- `GET /history?limit=N` → { items: [] } (du plus récent au plus ancien)

---

### Exécution locale (sans Docker)
- Dépannage rapide: `PYTHONPATH=. python orchestrator/main.py config/config.json`
- API locale: `uvicorn orchestrator.api:app_factory --factory --host 0.0.0.0 --port 8000`

---

### Git (préparation push)
- Initialisation locale: `git init && git checkout -b main`
- Commit initial: `git add -A && git commit -m "Mise en place Seeker: bandit, API, UI, Docker"`
- Ajouter le remote puis pousser: `git remote add origin <url> && git push -u origin main`


