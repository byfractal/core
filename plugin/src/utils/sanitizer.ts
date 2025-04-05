/**
 * HTML and CSS sanitization utilities to prevent XSS attacks and other security vulnerabilities
 * when converting HTML content to Figma nodes.
 */

/**
 * Sanitizes HTML content to prevent XSS attacks
 * @param htmlContent HTML string to sanitize
 * @returns Sanitized HTML string
 */
export function sanitizeHtml(htmlContent: string): string {
  // In a real implementation, we would use DOMPurify or another sanitization library
  // For now we're implementing a basic version

  // Create a DOM parser to handle the HTML
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlContent, "text/html");

  // Remove potentially dangerous elements
  const dangerousTags = ["script", "iframe", "object", "embed", "base", "form"];
  dangerousTags.forEach((tag) => {
    const elements = doc.getElementsByTagName(tag);
    for (let i = elements.length - 1; i >= 0; i--) {
      elements[i].parentNode?.removeChild(elements[i]);
    }
  });

  // Return sanitized HTML
  return doc.body.innerHTML;
}

/**
 * Sanitizes a CSS style object to prevent malicious code injection
 * @param cssStyle CSS style object to sanitize
 * @returns Sanitized CSS style object
 */
export function sanitizeCssStyle(
  cssStyle: Record<string, any>
): Record<string, any> {
  const sanitizedStyle: Record<string, any> = {};
  const dangerousProperties = [
    "expression",
    "eval",
    "javascript:",
    "behavior",
    "-moz-binding",
    "url(", // Filter URL expressions which could lead to loading external resources
    "position:fixed",
    "position:absolute",
  ];

  for (const [property, value] of Object.entries(cssStyle)) {
    // Skip dangerous CSS properties
    let isDangerous = false;

    // Check if the property itself is dangerous
    if (dangerousProperties.some((dp) => property.includes(dp))) {
      isDangerous = true;
    }

    // Check if the value contains dangerous content
    if (typeof value === "string") {
      if (dangerousProperties.some((dp) => value.includes(dp))) {
        isDangerous = true;
      }
    }

    // Only add safe properties
    if (!isDangerous) {
      sanitizedStyle[property] = value;
    }
  }

  return sanitizedStyle;
}

/**
 * Sanitizes HTML element attributes to prevent XSS attacks
 * @param attributes Object containing HTML attributes
 * @returns Sanitized attributes object
 */
export function sanitizeAttributes(
  attributes: Record<string, string>
): Record<string, string> {
  const sanitizedAttributes: Record<string, string> = {};
  const dangerousAttributes = [
    "on", // Catches onclick, onload, onerror, etc.
    "xmlns", // Can be used for XXE attacks
    "formaction",
    "xlink:href",
    "data-", // Be cautious with data attributes
    "src", // Needs special handling
    "href", // Needs special handling
  ];

  for (const [name, value] of Object.entries(attributes)) {
    // Skip event handlers and other dangerous attributes
    let isDangerous = false;

    // Check if the attribute name contains dangerous patterns
    for (const dangerousAttr of dangerousAttributes) {
      if (name.toLowerCase().startsWith(dangerousAttr)) {
        // Special handling for src and href
        if ((name === "src" || name === "href") && isSafeUrl(value)) {
          // Allow safe URLs
          isDangerous = false;
          break;
        } else {
          isDangerous = true;
          break;
        }
      }
    }

    // Only add safe attributes
    if (!isDangerous) {
      sanitizedAttributes[name] = value;
    }
  }

  return sanitizedAttributes;
}

/**
 * Checks if a URL is safe (not javascript: or data: except for images)
 * @param url URL to check
 * @returns True if the URL is safe
 */
function isSafeUrl(url: string): boolean {
  const lowerUrl = url.toLowerCase().trim();

  // Block javascript: and vbscript: protocols
  if (lowerUrl.startsWith("javascript:") || lowerUrl.startsWith("vbscript:")) {
    return false;
  }

  // Only allow image data URLs
  if (lowerUrl.startsWith("data:")) {
    return lowerUrl.startsWith("data:image/");
  }

  // Allow http, https, and relative URLs
  return (
    lowerUrl.startsWith("http:") ||
    lowerUrl.startsWith("https:") ||
    lowerUrl.startsWith("/") ||
    lowerUrl.startsWith("./") ||
    lowerUrl.startsWith("#")
  );
}

/**
 * Validates and sanitizes a complete HTML element and its children
 * @param element HTML element to sanitize
 * @returns Sanitized HTML element
 */
export function sanitizeHtmlElement(element: any): any {
  // Skip if no element
  if (!element) return null;

  // Check if element has a valid tag
  if (!element.tagName) return null;

  // Skip dangerous elements
  const dangerousTags = ["script", "iframe", "object", "embed", "base", "form"];
  if (dangerousTags.includes(element.tagName.toLowerCase())) {
    return null;
  }

  // Sanitize attributes and style
  const sanitizedAttributes = sanitizeAttributes(element.attributes || {});
  const sanitizedStyle = sanitizeCssStyle(element.style || {});

  // Sanitize children recursively
  const sanitizedChildren = element.children
    ? element.children
        .map((child: any) => sanitizeHtmlElement(child))
        .filter(Boolean)
    : [];

  // Return sanitized element
  return {
    ...element,
    attributes: sanitizedAttributes,
    style: sanitizedStyle,
    children: sanitizedChildren,
  };
}
