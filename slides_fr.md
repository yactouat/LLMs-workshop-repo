# DevFest 2025 : LLMs Locaux, RAG et Architectures Multi-Agents

Construire le Cerveau Interne de ACME Corp

---

## À mon propos

[Yacine Touati](https://www.linkedin.com/in/yactouat/)

Développeur logiciel et futuriste optimiste. Passionné par la tech, l'IA, le développement web et la Culture. Construction et enseignement de systèmes d'information. 🚀

Travaille actuellement chez Lamalo, une startup basée à Strasbourg, qui développe une application d'agrégateur d'IAs amélioré.

---

## La Mission

**Objectif :** Construire un système intelligent pour "ACME Corp" totalement hors ligne.

**Pourquoi en Local ?**
- Confidentialité (les données sensibles de l'entreprise ne quittent jamais votre infrastructure)
- Zéro coût de latence API (pas de tarification au token)
- Souveraineté des données (contrôle total sur vos données)

**La Stack :**
- **Moteur :** Ollama (Llama 3.1 / Qwen 3)
- **Orchestration :** LangChain (Le Squelette) & LangGraph (Le Cerveau)
- **Mémoire :** SQLite (Vectorielle avec l'extension VSS)

---

## Démo 1 : Hello World avec LLM Local

**Commande :** `python3 01_local_llm/hello_world.py [--thinking]`

**Ce Que Vous Verrez :**
- Interaction directe avec un LLM local via Ollama
- Le modèle tente de répondre : "Qui est le PDG de ACME Corp ?"
- Le modèle ne peut pas répondre car ACME Corp n'est pas dans ses données d'entraînement

**Qu'est-ce Que les Modèles "Thinking" ?**
- Ajoutez le flag `--thinking` pour voir le processus de raisonnement du modèle
- Le modèle expose sa chaîne de pensée interne avant de répondre
- Utile pour déboguer et comprendre le fonctionnement des LLMs

**Le Problème :**
Les LLMs ont une date limite de connaissances fixe. Ils ne peuvent pas répondre aux questions sur des informations privées ou des événements récents.

**La Solution :** RAG (Génération Augmentée par Récupération)

---

## Démo 2a : Ingestion RAG - Construction de la Base de Connaissances

**Commande :** `python3 02_rag_lcel/ingest.py`

**Ce Qui Se Passe :**
1. **Charger** la base de connaissances (politiques d'entreprise, info PDG, culture)
2. **Découper** le document sémantiquement
3. **Vectoriser** chaque morceau en vecteurs
4. **Stocker** les vecteurs dans SQLite avec l'extension VSS

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
1. Question → embedding vectoriel
2. Récupération des 5 morceaux les plus similaires depuis SQLite
3. Contexte + question → LLM
4. Le LLM génère la réponse

**Pourquoi LCEL ?**
- Composable (mixer les composants comme des LEGO)
- Lisible (flux de données clair)
- Optimisé (parallélisation automatique)

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

**Outils Disponibles :**
- `lookup_policy` : Interroger la base de connaissances (RAG)
- `search_tech_events` : Trouver des conférences

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

**Avantages :** Facile à déboguer, délégation claire, workflows orchestrés

**Inconvénients :** Goulot d'étranglement du superviseur, moins flexible

**Cas d'Usage :** Workflows prévisibles, tâches hiérarchiques

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

**Avantages :** Flexible, pas de goulot, collaboration créative

**Inconvénients :** Plus difficile à déboguer, risque de boucles, moins prévisible

**Cas d'Usage :** Tâches créatives, recherche exploratoire

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

**1. LLMs Locaux = Confidentialité + Coût Zéro**
- Fonctionne sur du matériel grand public
- Pas de dépendance au cloud

**2. Le RAG Comble les Lacunes de Connaissances**
- Les embeddings permettent la recherche sémantique
- SQLite VSS le rend accessible

**3. Les Graphes Permettent l'Intelligence**
- LangGraph : prise de décision adaptative
- ReAct : raisonnement + utilisation d'outils en boucles

**4. Les Systèmes Multi-Agents Passent à l'Échelle**
- Centralisé (Superviseur) : workflows prévisibles
- Décentralisé (Réseau) : collaboration créative

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
