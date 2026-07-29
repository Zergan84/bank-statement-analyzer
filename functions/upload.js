export async function onRequest(context) {
  const { request, env } = context;

  if (request.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const backend = env.API_BASE_URL;
  if (!backend) {
    return new Response(JSON.stringify({ error: "API_BASE_URL not configured" }), {
      status: 500,
      headers: { "content-type": "application/json" },
    });
  }

  const backendUrl = backend + "/upload";
  const resp = await fetch(backendUrl, {
    method: "POST",
    headers: request.headers,
    body: request.body,
  });

  const text = await resp.text();

  let data;
  try {
    data = JSON.parse(text);
  } catch {
    return new Response(text, { status: resp.status });
  }

  if (data && data.download_url) {
    const filename = data.download_url.split("/").pop();
    data.download_url = "/download/" + filename;
  }

  return new Response(JSON.stringify(data), {
    status: resp.status,
    headers: { "content-type": "application/json" },
  });
}
