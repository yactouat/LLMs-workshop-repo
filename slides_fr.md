# DevFest 2025 : LLMs Locaux, RAG et Architectures Multi-Agents

Construire le Cerveau Interne de ACME Corp

---

## À mon propos

[Yacine Touati](https://www.linkedin.com/in/yactouat/)

Développeur logiciel et futuriste optimiste. Passionné par la tech, l'IA, le développement web et la Culture. Construction et enseignement de systèmes d'information. 🚀

Travaille actuellement chez Lamalo, une startup basée à Strasbourg, qui développe une application d'agrégateur d'IAs amélioré.

---

## La Mission

**Objectif :** Construire un système intelligent pour "ACME Corp" avec des options de déploiement flexibles.

**Options de Fournisseur :**
- **Local (Ollama) :** Confidentialité d'abord, hors ligne, zéro coût d'API
  - Fonctionne sur votre matériel (8GB+ RAM recommandé)
  - Modèles Llama 3.1 / Qwen 3
  - Souveraineté complète des données
- **Cloud (Google AI Studio) :** Démarrage rapide, pas de configuration locale
  - Utilise le modèle Gemini 3 Flash Preview
  - Nécessite une clé API et une connexion internet

**La Stack :**
- **Moteur :** Ollama (local) OU Google AI Studio (cloud) - configurable via LLM_PROVIDER
- **Orchestration :** LangChain (Le Squelette) & LangGraph (Le Cerveau)
- **Mémoire :** SQLite (Vectorielle avec l'extension VSS)

---

## Démo 1 : Hello World avec LLM

**Commande :** `python3 01_local_llm/hello_world.py [--thinking]`

**Ce Que Vous Verrez :**
- Interaction directe avec un LLM (Ollama local OU Google cloud)
- Le modèle tente de répondre : "Qui est le PDG de ACME Corp ?"
- Le modèle ne peut pas répondre car ACME Corp n'est pas dans ses données d'entraînement

**Sélection du Fournisseur :**
- Par défaut : Ollama (local)
- Option cloud : Définissez `LLM_PROVIDER=google` dans le fichier `.env` avec `GOOGLE_API_KEY`

**Qu'est-ce Que les Modèles "Thinking" ?**
- Ajoutez le flag `--thinking` pour voir le processus de raisonnement du modèle
- Le modèle expose sa chaîne de pensée interne avant de répondre
- Ollama : Utilise qwen3 (configuré via OLLAMA_THINKING_MODEL)
- Google : Utilise gemini-3-flash-preview (configuré via GOOGLE_THINKING_MODEL)

**Le Problème :**
Les LLMs ont une date limite de connaissances fixe. Ils ne peuvent pas répondre aux questions sur des informations privées ou des événements récents.

**La Solution :** RAG (Génération Augmentée par Récupération)

---

## Démo 2a : Ingestion RAG - Construction de la Base de Connaissances

**Commande :** `python3 02_rag_lcel/ingest.py`

**Ce Qui Se Passe :**
1. **Charger** la base de connaissances (politiques d'entreprise, info PDG, culture)
2. **Découper** le document sémantiquement
3. **Vectoriser** chaque morceau en vecteurs (embeddings spécifiques au fournisseur)
4. **Stocker** les vecteurs dans SQLite avec l'extension VSS

**Embeddings par Fournisseur :**
- Ollama : nomic-embed-text
- Google : gemini-embedding-001

**Important :** Relancez `ingest.py` lors du changement de fournisseur - les embeddings ne sont pas compatibles !

**Pourquoi le RAG ?**
- Les LLMs ont du mal avec les grands contextes (10k+ tokens)
- RAG : Ne récupère que ce qui est pertinent (top 3-5 morceaux)

---

## Qu'est-ce Que les Embeddings Vectoriels ?

**Texte → Nombres :**
- Les mots et phrases deviennent des vecteurs dans un espace de haute dimension
- Significations similaires = Vecteurs similaires (mathématiquement)

**Exemple :**
```
"roi" - "homme" + "femme" ≈ "reine"
```

**Pourquoi les Embeddings Importent :**
- Permettent la **recherche sémantique** (par sens, pas seulement par mots-clés)
- "PDG" trouve "directeur général" sans correspondance exacte
- Fondement de la recherche IA moderne et du RAG

---

## Démo 2b : Requête RAG - LCEL en Action

**Commande :** `python3 02_rag_lcel/query.py [--interactive] [--question "VOTRE_QUESTION"] [--thinking]`

**LCEL = Langage d'Expression LangChain**

Pensez **pipes Linux** pour l'IA :
```python
chain = retriever | prompt | model | output_parser
```

**Comment Ça Marche :**
1. Question → embedding vectoriel (utilise le même fournisseur que ingest.py)
2. Récupération des 5 morceaux les plus similaires depuis SQLite
3. Contexte + question → LLM (Ollama ou Google)
4. Le LLM génère la réponse

**Pourquoi LCEL ?**
- Composable (mixer les composants comme des LEGO)
- Lisible (flux de données clair)
- Optimisé (parallélisation automatique)
- Agnostique du fournisseur (fonctionne avec Ollama et Google)

**Limitation :** Séquentiel (A → B → C). Et si vous avez besoin de boucles ?

---

## Démo 3 : Agent ReAct LangGraph - Quand les Chaînes Ne Suffisent Pas

**Commande :** `python3 03_langgraph_react/agent.py [--interactive] [--question "VOTRE_QUESTION"] [--thinking]`

**Chaîne vs. Graphe :**
| Chaîne (LCEL) | Graphe (LangGraph) |
|--------------|-------------------|
| Séquentiel | Cyclique (boucles) |
| Pipeline fixe | Décisions dynamiques |
| Recette linéaire | Organigramme |

**ReAct = Raisonnement + Action :**
```
[DÉBUT] → agent → décision?
                   ├─ besoin_outil → outils → agent (boucle)
                   └─ terminé → [FIN]
```

**Innovation Clé :**
- L'agent **choisit** quel outil utiliser
- Peut boucler plusieurs fois
- Raisonnement avant l'action
- Fonctionne avec les modèles Ollama et Google

**Outils Disponibles :**
- `lookup_policy` : Interroger la base de connaissances (RAG - utilise les mêmes embeddings que ingest.py)
- `search_tech_events` : Trouver des conférences

**Note :** Nécessite l'exécution de `ingest.py` d'abord avec le même fournisseur

---

## Démo 4 : Le Pattern Superviseur - Contrôle Centralisé

**Commande :** `python3 04_supervisor/supervisor.py [--interactive] [--question "VOTRE_QUESTION"] [--thinking]`

**Topologie :** Centralisée (Hub and Spoke)

```
        Chercheur ←─┐
              ↑      │
Utilisateur → Superviseur → Rédacteur
              ↓      │
        Vérificateur ┘
```

**Comment Ça Marche :**
1. Le superviseur reçoit la question
2. Délègue aux travailleurs spécialisés (Chercheur, Rédacteur, Vérificateur)
3. Le travailleur retourne les résultats
4. Le superviseur synthétise et répond

**Support des Fournisseurs :**
- Fonctionne avec les modèles Ollama et Google
- Tous les agents utilisent le même fournisseur (configuré via LLM_PROVIDER)
- L'agent Chercheur utilise le RAG (nécessite des embeddings correspondants)

**Avantages :** Facile à déboguer, délégation claire, workflows orchestrés

**Inconvénients :** Goulot d'étranglement du superviseur, moins flexible

**Cas d'Usage :** Workflows prévisibles, tâches hiérarchiques

**Note :** Nécessite l'exécution de `ingest.py` d'abord avec le même fournisseur

---

## Démo 5 : Le Pattern Réseau/Essaim - Collaboration Décentralisée

**Commande :** `python3 05_network/network.py [--interactive] [--question "VOTRE_QUESTION"] [--thinking]`

**Topologie :** Décentralisée (Maillage / Pair-à-Pair)

```
Chercheur ←→ Rédacteur
    ↕          ↕
Vérificateur ←→ Coordinateur
```

**Comment Ça Marche :**
- Les agents communiquent **directement** entre eux
- N'importe quel agent peut passer la main à un autre
- Pas de coordinateur central
- Collaboration auto-organisée
- Utilise les outils `transfer_to_*()` pour les passages pair-à-pair

**Support des Fournisseurs :**
- Fonctionne avec les modèles Ollama et Google
- Tous les agents utilisent le même fournisseur (configuré via LLM_PROVIDER)
- L'agent Chercheur utilise le RAG (nécessite des embeddings correspondants)

**Avantages :** Flexible, pas de goulot, collaboration créative

**Inconvénients :** Plus difficile à déboguer, risque de boucles, moins prévisible

**Cas d'Usage :** Tâches créatives, recherche exploratoire

**Note :** Nécessite l'exécution de `ingest.py` d'abord avec le même fournisseur

---

## Systèmes Multi-Agents Centralisés vs. Décentralisés

**Centralisé (Superviseur) :**
- Un agent contrôle le routage
- Topologie en étoile
- Exécution prévisible
- Exemple : Manager assigne les tâches à l'équipe

**Décentralisé (Réseau/Essaim) :**
- Les agents se coordonnent en pair-à-pair
- Topologie maillée
- Exécution dynamique
- Exemple : L'équipe s'auto-organise les tâches

**Différence Clé :** Qui décide de la prochaine étape ?

---

## Comparaison Architecturale : Superviseur vs. Réseau

| Aspect | Superviseur | Réseau |
|--------|-----------|---------|
| **Contrôle** | Centralisé | Décentralisé |
| **Routage** | Le manager décide | Les agents s'auto-coordonnent |
| **Visibilité** | Facile à tracer | Chemins complexes |
| **Flexibilité** | Structuré | Hautement adaptatif |
| **Idéal Pour** | Workflows prévisibles | Exploration créative |

**Hybride :** Combinez les deux (ex: Superviseurs par département, réseaux à l'intérieur)

---

## Horizons Futurs : Au-delà du RAG Vectoriel

**GraphRAG :**
- RAG standard : Récupère des morceaux de texte
- GraphRAG : Récupère les **relations** entre entités
- Exemple : "Qui rend compte au PDG ?" nécessite de la structure, pas juste de la similarité

**Graphes de Connaissances :**
- Entités + Relations (rend_compte_à, définit, impacte)
- Raisonnement sur des connaissances structurées
- Outils : Neo4j, triplets RDF, graphes de propriétés

**RAG Agentique :**
- Les agents interrogent les bases vectorielles **ET** les graphes de connaissances
- Capacités de raisonnement plus sophistiquées

---

## Points Clés à Retenir

**1. Options de Déploiement Flexibles**
- Local (Ollama) : Confidentialité, coût zéro, fonctionnement hors ligne
- Cloud (Google) : Démarrage rapide, pas d'exigences matérielles
- Changement facile entre fournisseurs via LLM_PROVIDER

**2. Le RAG Comble les Lacunes de Connaissances**
- Les embeddings permettent la recherche sémantique
- SQLite VSS le rend accessible
- Embeddings spécifiques au fournisseur (doivent correspondre entre ingest et query)

**3. Les Graphes Permettent l'Intelligence**
- LangGraph : prise de décision adaptative
- ReAct : raisonnement + utilisation d'outils en boucles
- Fonctionne de manière transparente avec les modèles locaux et cloud

**4. Les Systèmes Multi-Agents Passent à l'Échelle**
- Centralisé (Superviseur) : workflows prévisibles
- Décentralisé (Réseau) : collaboration créative
- Architecture agnostique du fournisseur

**5. Futur : GraphRAG + Architectures Hybrides**

---

## Ressources & Prochaines Étapes

**Dépôt de l'Atelier :**
https://github.com/yactouat/devfest-2025-local-llms-workshop

**Outils Essentiels :**
- Ollama : https://ollama.com
- LangChain : https://python.langchain.com
- LangGraph : https://langchain-ai.github.io/langgraph
- SQLite VSS : https://github.com/asg017/sqlite-vss

**Continuer l'Apprentissage :**
- **[LangChain Academy](https://academy.langchain.com/)** - Cours gratuits sur LangChain & LangGraph
- Expérimentez avec les 5 démos de cet atelier
- Ajoutez des checkpoints de mémoire à vos graphes
- Construisez votre propre base de connaissances
- Créez des outils personnalisés pour votre domaine

**Merci !**

*Maintenant allez construire quelque chose d'intelligent, privé et local.*
