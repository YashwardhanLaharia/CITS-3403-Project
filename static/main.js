const CATEGORY_ICONS = {
  Food: '🍔',
  Transport: '🚗',
  Accommodation: '🏠',
  Entertainment: '🎬',
  Utilities: '💡',
};

function categoryIcon(cat) {
  return CATEGORY_ICONS[cat] || '📦';
}

function renderMemberBalances(members) {
  const grid = document.getElementById('member-balances-grid');
  if (!grid) return;
  if (!members.length) {
    grid.innerHTML = `
      <div class="group-card" style="border:1px dashed var(--border);display:flex;align-items:center;justify-content:center;min-height:140px;">
        <div style="text-align:center;color:var(--text-muted);">
          <i class="bi bi-cash-stack" style="font-size:2rem;"></i>
          <div style="margin-top:8px;">No expenses recorded yet.</div>
        </div>
      </div>`;
    return;
  }
  grid.innerHTML = members.map(m => {
    const color = m.balance >= 0 ? 'var(--accent)' : 'var(--danger, #e05252)';
    const balanceText = m.balance >= 0
      ? `Owed $${m.balance.toFixed(2)}`
      : `Owes $${Math.abs(m.balance).toFixed(2)}`;
    return `
      <div class="group-card">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
          <div class="avatar-sm">${m.initials}</div>
          <div class="group-card-name">${m.name}</div>
        </div>
        <div class="group-card-meta">Paid: $${m.amount_paid.toFixed(2)}</div>
        <div class="group-card-balance" style="color:${color}">${balanceText}</div>
      </div>`;
  }).join('');
}

function renderExpenseFeed(expenses) {
  const feed = document.getElementById('expense-feed');
  if (!feed) return;
  if (!expenses.length) {
    feed.innerHTML = `
      <div class="archived-card">
        <div class="archived-icon">📝</div>
        <div>
          <div class="archived-name">No activity yet</div>
          <div class="archived-meta">Add an expense to get started</div>
        </div>
      </div>`;
    return;
  }
  feed.innerHTML = expenses.map(e => {
    // Parse as local date to avoid timezone shift
    const [year, month, day] = e.date.split('-');
    const d = new Date(year, month - 1, day);
    const dateStr = d.toLocaleDateString('en-AU', { day: '2-digit', month: 'short', year: 'numeric' });
    return `
      <div class="archived-card">
        <div class="archived-icon">${categoryIcon(e.category)}</div>
        <div>
          <div class="archived-name">${e.description}</div>
          <div class="archived-meta">$${e.amount.toFixed(2)} &middot; ${e.category} &middot; ${dateStr} &middot; paid by ${e.paid_by}</div>
        </div>
      </div>`;
  }).join('');
}

function renderSettlement(transfers) {
  const preview = document.getElementById('settlement-preview');
  if (!preview) return;
  if (!transfers.length) {
    preview.innerHTML = `
      <div class="archived-card">
        <div class="archived-icon"><i class="bi bi-arrow-left-right"></i></div>
        <div>
          <div class="archived-name">All settled up</div>
          <div class="archived-meta">No outstanding balances</div>
        </div>
      </div>`;
    return;
  }
  preview.innerHTML = transfers.map(t => `
    <div class="archived-card">
      <div class="archived-icon"><i class="bi bi-arrow-right-circle"></i></div>
      <div>
        <div class="archived-name">${t.from} → ${t.to}</div>
        <div class="archived-meta">$${t.amount.toFixed(2)}</div>
      </div>
      <button class="btn-settle" data-from="${t.from_user_id}" data-to="${t.to_user_id}" data-amount="${t.amount}">
        <i class="bi bi-check-circle"></i> Mark Paid
      </button>
    </div>`).join('');
}

function renderPaymentHistory(payments) {
  const container = document.getElementById('payment-history');
  if (!container) return;
  if (!payments.length) {
    container.innerHTML = `
      <div class="archived-card">
        <div class="archived-icon"><i class="bi bi-clock-history"></i></div>
        <div>
          <div class="archived-name">No payments yet</div>
          <div class="archived-meta">Settle up using the buttons above</div>
        </div>
      </div>`;
    return;
  }
  container.innerHTML = payments.map(p => {
    const [year, month, day, hour, min] = p.created_at.split(/[-T:]/);
    const d = new Date(year, month - 1, day, hour, min);
    const dateStr = d.toLocaleDateString('en-AU', { day: '2-digit', month: 'short', year: 'numeric' });
    return `
      <div class="archived-card">
        <div class="archived-icon"><i class="bi bi-check-circle-fill" style="color:var(--accent);"></i></div>
        <div>
          <div class="archived-name">${p.from_name} → ${p.to_name}</div>
          <div class="archived-meta">$${p.amount.toFixed(2)} · ${dateStr}</div>
        </div>
      </div>`;
  }).join('');
}

async function recordPayment(groupId, fromUserId, toUserId, amount) {
  const csrfToken = document.querySelector('[name=csrf_token]')?.value || '';
  const response = await fetch(`/groups/${groupId}/payments/add`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify({
      from_user_id: fromUserId,
      to_user_id: toUserId,
      amount: amount,
    }),
  });
  const data = await response.json();
  return data;
}

function renderGroupSummary(group, memberCount) {
  const sub = document.getElementById('group-summary');
  if (!sub) return;
  const plural = memberCount !== 1 ? 's' : '';
  sub.textContent = `${memberCount} member${plural} · ${group.currency} · Total spent: $${group.total_spent.toFixed(2)}`;
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('addExpenseForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const csrfToken = form.querySelector('[name=csrf_token]').value;
    const action = form.action;
    const match = action.match(/\/groups\/(\d+)\//);
    if (!match) return;
    const groupId = match[1];

    const existingAlert = form.querySelector('.ajax-error');
    if (existingAlert) existingAlert.remove();

    let data;
    try {
      const response = await fetch(action, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken,
        },
        body: new FormData(form),
      });
      data = await response.json();
    } catch {
      return;
    }

    if (!data.success) {
      const alert = document.createElement('div');
      alert.className = 'ajax-error';
      alert.style.cssText = 'color:var(--danger,#e05252);margin-bottom:1rem;font-size:0.875rem;';
      alert.innerHTML = data.errors.map(err => `<div>${err}</div>`).join('');
      form.querySelector('.modal-body').prepend(alert);
      return;
    }

    const modal = bootstrap.Modal.getInstance(document.getElementById('addExpenseModal'));
    if (modal) modal.hide();
    form.reset();

    try {
      const fresh = await fetch(`/groups/${groupId}/data`).then(r => r.json());
      renderMemberBalances(fresh.members);
      renderExpenseFeed(fresh.expenses);
      renderSettlement(fresh.transfers);
      renderPaymentHistory(fresh.payments);
      renderGroupSummary(fresh.group, fresh.members.length);
    } catch {
      // Data fetch failed — page still functional, data will update on next reload
    }
  });

  document.querySelectorAll('.archived-grid').forEach(grid => {
    grid.addEventListener('click', async (e) => {
      const btn = e.target.closest('.btn-settle');
      if (!btn) return;

      const currentUserId = parseInt(document.querySelector('.page-body')?.dataset.currentUserId || '0', 10);
      const fromUserId = parseInt(btn.dataset.from, 10);
      const toUserId = parseInt(btn.dataset.to, 10);
      const amount = btn.dataset.amount;

      const payerId = currentUserId === fromUserId ? fromUserId : (currentUserId === toUserId ? toUserId : fromUserId);
      const payeeId = currentUserId === fromUserId ? toUserId : (currentUserId === toUserId ? fromUserId : toUserId);

      if (currentUserId !== fromUserId && currentUserId !== toUserId) {
        return;
      }

      const match = window.location.pathname.match(/\/groups\/(\d+)/);
      if (!match) return;
      const groupId = match[1];

      btn.disabled = true;
      btn.innerHTML = '<i class="bi bi-hourglass-split"></i>...';

      const result = await recordPayment(groupId, payerId, payeeId, amount);

      if (result.success) {
        try {
          const fresh = await fetch(`/groups/${groupId}/data`).then(r => r.json());
          renderMemberBalances(fresh.members);
          renderSettlement(fresh.transfers);
          renderPaymentHistory(fresh.payments);
        } catch {
          window.location.reload();
        }
      } else {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-check-circle"></i> Mark Paid';
        const toast = document.createElement('div');
        toast.className = 'alert alert-danger';
        toast.textContent = result.errors?.[0] || 'Payment failed';
        document.querySelector('.page-body')?.prepend(toast);
        setTimeout(() => toast.remove(), 4000);
      }
    });
  });
});
