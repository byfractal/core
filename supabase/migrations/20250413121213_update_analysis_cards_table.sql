-- Migration : Mise à jour de la table analysis_cards pour ajouter les champs requis par AnalysisCardComponent

-- Ajout des nouvelles colonnes
ALTER TABLE analysis_cards
ADD COLUMN IF NOT EXISTS root_cause TEXT,
ADD COLUMN IF NOT EXISTS supporting_metric TEXT,
ADD COLUMN IF NOT EXISTS contextual_data JSONB,
ADD COLUMN IF NOT EXISTS warning_message TEXT,
ADD COLUMN IF NOT EXISTS recommended_fix TEXT,
ADD COLUMN IF NOT EXISTS impact_estimate TEXT,
ADD COLUMN IF NOT EXISTS sources TEXT[],
ADD COLUMN IF NOT EXISTS is_new BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS optimization_number INTEGER;

-- Mise à jour des niveaux de sévérité pour correspondre aux nouvelles spécifications
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

-- Mettre à jour les anciennes valeurs de sévérité pour correspondre aux nouvelles
UPDATE analysis_cards
SET severity = CASE 
    WHEN severity = 'LOW' THEN 'MINOR'
    WHEN severity = 'MEDIUM' THEN 'NEEDS_IMPROVEMENT'
    WHEN severity = 'HIGH' THEN 'UNDERPERFORMING'
    WHEN severity = 'CRITICAL' THEN 'CRITICAL_UX_DEBT'
    ELSE 'NEEDS_IMPROVEMENT'
END;

-- Ajout d'un commentaire à la table
COMMENT ON TABLE analysis_cards IS 'Cartes d''analyse UX/UI pour les composants Figma';

-- Ajout de commentaires aux nouvelles colonnes
COMMENT ON COLUMN analysis_cards.root_cause IS 'Explication UX simple et directe du problème';
COMMENT ON COLUMN analysis_cards.supporting_metric IS 'Métrique principale supportant l''analyse';
COMMENT ON COLUMN analysis_cards.contextual_data IS 'Données contextuelles incluant benchmarks, type de page, nombre d''utilisateurs';
COMMENT ON COLUMN analysis_cards.warning_message IS 'Impact UX explicite';
COMMENT ON COLUMN analysis_cards.recommended_fix IS 'Action claire et basée sur preuves';
COMMENT ON COLUMN analysis_cards.impact_estimate IS 'Projection d''amélioration précise (%)';
COMMENT ON COLUMN analysis_cards.sources IS 'Sources comme NN Group, Lucidpark';
COMMENT ON COLUMN analysis_cards.is_new IS 'Si l''insight est affiché pour la première fois (pour animation shine)';
COMMENT ON COLUMN analysis_cards.optimization_number IS 'Numéro séquentiel de l''optimisation'; 