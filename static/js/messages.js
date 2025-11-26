document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('messages-container');
  if (!container) return;

  let page = parseInt(container.dataset.page || '0', 10);
  let loading = false;
  let more = container.dataset.hasMore === 'True' || container.dataset.hasMore === 'true';

  // Scroll to bottom initially (show newest messages)
  container.scrollTop = container.scrollHeight;

  async function loadPage(nextPage) {
    if (loading) return;
    loading = true;
    try {
      const groupId = container.dataset.groupId;
      const res = await fetch(`/group/${groupId}/posts?page=${nextPage}`);
      if (!res.ok) return;
      const data = await res.json();
      if (!data.posts || data.posts.length === 0) {
        more = data.more;
        return;
      }

      // remember current scroll height to maintain position after prepending
      const prevHeight = container.scrollHeight;

      // prepend posts (older ones) to top
      for (let i = 0; i < data.posts.length; i++) {
        const p = data.posts[i];
        const el = renderMessage(p.author, p.text);
        container.insertBefore(el, container.firstChild);
      }

      // adjust scroll to keep view stable
      const newHeight = container.scrollHeight;
      container.scrollTop = newHeight - prevHeight;

      page = data.page;
      more = data.more;
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }

  function renderMessage(author, text) {
    const card = document.createElement('div');
    card.className = 'card mb-2';
    const body = document.createElement('div');
    body.className = 'card-body';
    const h = document.createElement('h6');
    h.className = 'card-subtitle mb-2 text-muted';
    h.textContent = author;
    const p = document.createElement('p');
    p.className = 'card-text';
    // preserve newlines: split and append text nodes with <br>
    const lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
      p.appendChild(document.createTextNode(lines[i]));
      if (i < lines.length - 1) p.appendChild(document.createElement('br'));
    }
    body.appendChild(h);
    body.appendChild(p);
    card.appendChild(body);
    return card;
  }

  // when scrolling near the top, load older posts (next page)
  container.addEventListener('scroll', function () {
    if (container.scrollTop < 120 && more && !loading) {
      loadPage(page + 1);
    }
  });
});
