export async function onRequest(context) {
  const { request, env } = context;
  const backend = env.API_BASE_URL || "http://localhost:8000";

  const url = new URL(request.url);
  const backendUrl = `${backend}/upload`;

  const headers = new Headers(request.headers);
  headers.delete("host");

  const resp = await fetch(backendUrl, {
    method: "POST",
    headers,
    body: request.body,
    duplex: "half",
  });

  const data = await resp.json();
  if (data.download_url) {
    data.download_url = `/download/${data.download_url.split("/").pop()}`;
  }

  return new Response(JSON.stringify(data), {
    status: resp.status,
    headers: { "content-type": "application/json" },
  });
}
