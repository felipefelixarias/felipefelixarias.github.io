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
})();
