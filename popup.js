const statusEl = document.getElementById("status");
const feedContainer = document.getElementById("feed-container");
const urlDisplay = document.getElementById("url-display");
const copyBtn = document.getElementById("copy-btn");

const showError = (msg) => {
  statusEl.textContent = msg;
  statusEl.style.display = "block";
  feedContainer.style.display = "none";
};

const showFeed = (url) => {
  statusEl.style.display = "none";
  urlDisplay.textContent = url;
  feedContainer.style.display = "block";
};

chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
  if (!tab?.id) {
    showError("No active tab found.");
    return;
  }

  chrome.scripting.executeScript(
    {
      target: { tabId: tab.id },
      func: async () => {
        const res = await fetch(location.href);
        const html = await res.text();
        const doc = new DOMParser().parseFromString(html, "text/html");
        const link = doc.querySelector('link[type="application/rss+xml"]');
        return link ? link.href : null;
      },
    },
    (results) => {
      if (chrome.runtime.lastError) {
        showError("Could not access this page.");
        return;
      }
      const url = results?.[0]?.result;
      if (!url) {
        showError("No RSS feed found on this page.");
        return;
      }
      showFeed(url);
    }
  );
});

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(urlDisplay.textContent).then(() => {
    copyBtn.textContent = "Copied!";
    copyBtn.classList.add("copied");
    setTimeout(() => {
      copyBtn.textContent = "Copy URL";
      copyBtn.classList.remove("copied");
    }, 1500);
  });
});
