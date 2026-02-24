async function captureEvent(baseUrl, orgId, eventId, payload) {
  const res = await fetch(${baseUrl}/events, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ org_id: orgId, event_id: eventId, payload })
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(LICITRA captureEvent failed:  );
  }
  return await res.json();
}

module.exports = { captureEvent };
