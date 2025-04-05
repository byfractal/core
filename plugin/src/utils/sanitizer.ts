/**
 * HTML and CSS sanitization utilities to prevent XSS attacks and other security vulnerabilities
 * when converting HTML content to Figma nodes.
 */
import { HtmlElementInterface, CssStyleInterface } from "../types/interfaces";

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
): CssStyleInterface {
  const sanitizedStyle: Record<string, any> = {};
  const dangerousProperties = [
    "expression",
    "eval",
    "javascript:",
    "behavior",
    "-moz-binding",
    "url(",
  ];

  // Filtrer les propriétés dangereuses
  for (const [property, value] of Object.entries(cssStyle)) {
    let isDangerous = false;

    if (dangerousProperties.some((dp) => property.includes(dp))) {
      isDangerous = true;
    }

    if (typeof value === "string") {
      if (dangerousProperties.some((dp) => value.includes(dp))) {
        isDangerous = true;
      }
    }

    if (!isDangerous) {
      sanitizedStyle[property] = value;
    }
  }

  return sanitizedStyle as CssStyleInterface;
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
    "on",
    "xmlns",
    "formaction",
    "xlink:href",
    "data-",
    "src",
    "href",
  ];

  for (const [name, value] of Object.entries(attributes)) {
    let isDangerous = false;

    for (const dangerousAttr of dangerousAttributes) {
      if (name.toLowerCase().startsWith(dangerousAttr)) {
        if ((name === "src" || name === "href") && isSafeUrl(value)) {
          isDangerous = false;
          break;
        } else {
          isDangerous = true;
          break;
        }
      }
    }

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

  if (lowerUrl.startsWith("javascript:") || lowerUrl.startsWith("vbscript:")) {
    return false;
  }

  if (lowerUrl.startsWith("data:")) {
    return lowerUrl.startsWith("data:image/");
  }

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
