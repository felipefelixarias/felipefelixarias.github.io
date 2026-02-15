/*
 * Google Analytics 4 bootstrap for this static site.
 * Replace GA_MEASUREMENT_ID with your real value from Google Analytics.
 */
(function initGoogleAnalytics() {
  "use strict";

  var GA_MEASUREMENT_ID = "G-6R32CPXR2P";

  if (!GA_MEASUREMENT_ID || GA_MEASUREMENT_ID === "G-XXXXXXXXXX") {
    return;
  }

  var script = document.createElement("script");
  script.async = true;
  script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_MEASUREMENT_ID);
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() {
    window.dataLayer.push(arguments);
  };

  window.gtag("js", new Date());
  window.gtag("config", GA_MEASUREMENT_ID, {
    anonymize_ip: true,
    send_page_view: true
  });

  function trackEvent(eventName, params) {
    if (typeof window.gtag !== "function") {
      return;
    }
    window.gtag("event", eventName, params || {});
  }

  function normalizePath(pathname) {
    var path = pathname || "/";
    path = path.toLowerCase();
    if (path.endsWith("/index.html")) {
      path = path.slice(0, -10);
    }
    if (!path.endsWith("/")) {
      path += "/";
    }
    return path;
  }

  function getProjectSlug(pathname) {
    var normalizedPath = normalizePath(pathname);
    var projectPaths = {
      "/marovi/": "marovi",
      "/acprm/": "acprm",
      "/multi-perspective-navigation/": "multi-perspective-navigation",
      "/multi-sentence-relation-extraction/": "multi-sentence-relation-extraction",
      "/video-as-a-sensor/": "video-as-a-sensor"
    };
    return projectPaths[normalizedPath] || null;
  }

  document.addEventListener("click", function handleTrackedLinkClick(event) {
    var eventTarget = event.target;
    var element = eventTarget && eventTarget.nodeType === 1 ? eventTarget : eventTarget && eventTarget.parentElement;
    if (!element || typeof element.closest !== "function") {
      return;
    }

    var anchor = element.closest("a[href]");
    if (!anchor) {
      return;
    }

    var href = anchor.getAttribute("href");
    if (!href || href.charAt(0) === "#") {
      return;
    }

    var linkUrl;
    try {
      linkUrl = new URL(anchor.href, window.location.href);
    } catch (error) {
      return;
    }

    if (linkUrl.protocol === "mailto:" || linkUrl.protocol === "tel:" || linkUrl.protocol === "javascript:") {
      return;
    }

    var linkText = (anchor.textContent || "").trim().replace(/\s+/g, " ").slice(0, 100);
    var currentPath = normalizePath(window.location.pathname);

    if (linkUrl.pathname.endsWith("/data/FFA_resume.pdf") || linkUrl.pathname.endsWith("FFA_resume.pdf")) {
      trackEvent("resume_download", {
        link_text: linkText,
        page_path: currentPath
      });
      return;
    }

    if (linkUrl.origin !== window.location.origin) {
      trackEvent("outbound_link_click", {
        link_url: linkUrl.href,
        link_domain: linkUrl.hostname,
        link_text: linkText,
        page_path: currentPath
      });
      return;
    }

    var projectSlug = getProjectSlug(linkUrl.pathname);
    if (projectSlug) {
      trackEvent("project_page_click", {
        project_slug: projectSlug,
        destination_path: normalizePath(linkUrl.pathname),
        link_text: linkText,
        page_path: currentPath
      });
    }
  });
})();
