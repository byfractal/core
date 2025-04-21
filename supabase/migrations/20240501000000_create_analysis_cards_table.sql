-- Migration : Création de la table analysis_cards pour stocker les cartes d'analyse UX/UI

-- Création d'un type personnalisé pour la sévérité
DO $$
BEGIN
    -- Vérifier si le type severity_level existe déjà
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'severity_level') THEN
        CREATE TYPE severity_level AS ENUM (
            'MINOR',
            'NEEDS_IMPROVEMENT',
            'UNDERPERFORMING',
            'CRITICAL_UX_DEBT'
        );
    END IF;
END
$$;

-- Création de la table analysis_cards
CREATE TABLE IF NOT EXISTS analysis_cards (
    id UUID PRIMARY KEY,
    figma_file_key TEXT NOT NULL,
    node_id TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    supporting_metric TEXT NOT NULL,
    contextual_data JSONB NOT NULL DEFAULT '{}',
    warning_message TEXT NOT NULL,
    recommended_fix TEXT NOT NULL,
    impact_estimate TEXT NOT NULL,
    sources TEXT[] NOT NULL DEFAULT '{}',
    severity TEXT NOT NULL DEFAULT 'NEEDS_IMPROVEMENT',
    tags TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_new BOOLEAN NOT NULL DEFAULT TRUE,
    optimization_number INTEGER
);

-- Ajout de commentaires
COMMENT ON TABLE analysis_cards IS 'Cartes d''analyse UX/UI pour les composants Figma';
COMMENT ON COLUMN analysis_cards.id IS 'Identifiant unique de la carte d''analyse';
COMMENT ON COLUMN analysis_cards.figma_file_key IS 'Clé du fichier Figma associé';
COMMENT ON COLUMN analysis_cards.node_id IS 'ID du nœud Figma associé';
COMMENT ON COLUMN analysis_cards.title IS 'Titre de la carte d''analyse';
COMMENT ON COLUMN analysis_cards.description IS 'Description détaillée de l''analyse';
COMMENT ON COLUMN analysis_cards.root_cause IS 'Explication UX simple et directe du problème';
COMMENT ON COLUMN analysis_cards.supporting_metric IS 'Métrique principale supportant l''analyse';
COMMENT ON COLUMN analysis_cards.contextual_data IS 'Données contextuelles incluant benchmarks, type de page, nombre d''utilisateurs';
COMMENT ON COLUMN analysis_cards.warning_message IS 'Impact UX explicite';
COMMENT ON COLUMN analysis_cards.recommended_fix IS 'Action claire et basée sur preuves';
COMMENT ON COLUMN analysis_cards.impact_estimate IS 'Projection d''amélioration précise (%)';
COMMENT ON COLUMN analysis_cards.sources IS 'Sources comme NN Group, Lucidpark';
COMMENT ON COLUMN analysis_cards.severity IS 'Niveau de sévérité de l''analyse';
COMMENT ON COLUMN analysis_cards.tags IS 'Tags pour filtrer et catégoriser les analyses';
COMMENT ON COLUMN analysis_cards.created_at IS 'Date et heure de création de la carte';
COMMENT ON COLUMN analysis_cards.is_new IS 'Si l''insight est affiché pour la première fois (pour animation shine)';
COMMENT ON COLUMN analysis_cards.optimization_number IS 'Numéro séquentiel de l''optimisation';

-- Création d'index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_analysis_cards_figma_file_key ON analysis_cards(figma_file_key);
CREATE INDEX IF NOT EXISTS idx_analysis_cards_node_id ON analysis_cards(node_id);
CREATE INDEX IF NOT EXISTS idx_analysis_cards_severity ON analysis_cards(severity);
CREATE INDEX IF NOT EXISTS idx_analysis_cards_created_at ON analysis_cards(created_at);

-- Activer la sécurité au niveau des lignes (RLS)
ALTER TABLE analysis_cards ENABLE ROW LEVEL SECURITY;

-- Créer une politique qui autorise toutes les opérations pour tous les utilisateurs
-- Dans un environnement de production, vous devriez restreindre l'accès selon vos besoins
CREATE POLICY analysis_cards_policy ON analysis_cards
    USING (true)
    WITH CHECK (true); 