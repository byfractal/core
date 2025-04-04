/**
 * Applique des propriétés de texte à un nœud Texte
 * @param textNode Nœud Texte à modifier
 * @param text Propriétés de texte à appliquer
 */
private static async applyTextProperties(
  textNode: TextNode,
  text: DesignChangeInterface['properties']['text']
): Promise<void> {
  if (!text) return;

  // Charger la police si nécessaire
  if (text.fontFamily || text.fontWeight) {
    const fontFamily = text.fontFamily || 'Inter';
    const fontWeight = text.fontWeight ? 
      (text.fontWeight > 600 ? 'Bold' : 'Regular') : 
      'Regular';
    
    try {
      await figma.loadFontAsync({ family: fontFamily, style: fontWeight });
      textNode.fontName = { family: fontFamily, style: fontWeight };
    } catch (error) {
      console.warn(`Failed to load font: ${fontFamily} ${fontWeight}`);
      // Essayer avec une police de secours
      await figma.loadFontAsync({ family: 'Inter', style: 'Regular' });
      textNode.fontName = { family: 'Inter', style: 'Regular' };
    }
  }

  // Définir le contenu du texte
  if (text.content !== undefined) {
    textNode.characters = text.content;
  }

  // Définir les autres propriétés de texte
  if (text.fontSize !== undefined) {
    textNode.fontSize = text.fontSize;
  }

  if (text.letterSpacing !== undefined) {
    textNode.letterSpacing = { value: text.letterSpacing, unit: 'PIXELS' };
  }

  if (text.lineHeight !== undefined) {
    if (typeof text.lineHeight === 'number') {
      textNode.lineHeight = { value: text.lineHeight, unit: 'PIXELS' };
    } else {
      textNode.lineHeight = text.lineHeight;
    }
  }

  if (text.textAlign !== undefined) {
    switch (text.textAlign) {
      case 'LEFT':
        textNode.textAlignHorizontal = 'LEFT';
        break;
      case 'CENTER':
        textNode.textAlignHorizontal = 'CENTER';
        break;
      case 'RIGHT':
        textNode.textAlignHorizontal = 'RIGHT';
        break;
      case 'JUSTIFIED':
        textNode.textAlignHorizontal = 'JUSTIFIED';
        break;
    }
  }

  if (text.textCase !== undefined) {
    switch (text.textCase) {
      case 'ORIGINAL':
        textNode.textCase = 'ORIGINAL';
        break;
      case 'UPPER':
        textNode.textCase = 'UPPER';
        break;
      case 'LOWER':
        textNode.textCase = 'LOWER';
        break;
      case 'TITLE':
        textNode.textCase = 'TITLE';
        break;
    }
  }

  if (text.textDecoration !== undefined) {
    switch (text.textDecoration) {
      case 'NONE':
        textNode.textDecoration = 'NONE';
        break;
      case 'UNDERLINE':
        textNode.textDecoration = 'UNDERLINE';
        break;
      case 'STRIKETHROUGH':
        textNode.textDecoration = 'STRIKETHROUGH';
        break;
    }
  }
}

/**
 * Applique des propriétés de mise en page à un nœud Figma
 * @param node Nœud à modifier
 * @param layout Propriétés de mise en page à appliquer
 */
private static applyLayoutProperties(
  node: SceneNode,
  layout: DesignChangeInterface['properties']['layout']
): void {
  if (!layout) return;

  // Position
  if (layout.x !== undefined) {
    node.x = layout.x;
  }
  
  if (layout.y !== undefined) {
    node.y = layout.y;
  }

  // Dimensions (si non gérées par resize)
  if (layout.width !== undefined && layout.height !== undefined) {
    if ('resize' in node) {
      node.resize(layout.width, layout.height);
    }
  } else if (layout.width !== undefined) {
    if ('resize' in node) {
      node.resize(layout.width, node.height);
    }
  } else if (layout.height !== undefined) {
    if ('resize' in node) {
      node.resize(node.width, layout.height);
    }
  }

  // Rotation
  if (layout.rotation !== undefined && 'rotation' in node) {
    node.rotation = layout.rotation;
  }

  // Contraintes
  if (layout.constraints && 'constraints' in node) {
    const { horizontal, vertical } = layout.constraints;
    
    if (horizontal) {
      switch (horizontal) {
        case 'LEFT':
          node.constraints.horizontal = 'MIN';
          break;
        case 'RIGHT':
          node.constraints.horizontal = 'MAX';
          break;
        case 'CENTER':
          node.constraints.horizontal = 'CENTER';
          break;
        case 'SCALE':
          node.constraints.horizontal = 'SCALE';
          break;
        case 'STRETCH':
          node.constraints.horizontal = 'STRETCH';
          break;
      }
    }
    
    if (vertical) {
      switch (vertical) {
        case 'TOP':
          node.constraints.vertical = 'MIN';
          break;
        case 'BOTTOM':
          node.constraints.vertical = 'MAX';
          break;
        case 'CENTER':
          node.constraints.vertical = 'CENTER';
          break;
        case 'SCALE':
          node.constraints.vertical = 'SCALE';
          break;
        case 'STRETCH':
          node.constraints.vertical = 'STRETCH';
          break;
      }
    }
  }
} 