export async function onRequest(context) {
  const { request, env, params } = context;
  const backend = env.API_BASE_URL || "http://localhost:8000";

  const backendUrl = `${backend}/download/${params.filename}`;

  const resp = await fetch(backendUrl);
  const blob = await resp.blob();

  return new Response(blob, {
    status: resp.status,
    headers: {
      "content-type": resp.headers.get("content-type") || "application/octet-stream",
      "content-disposition": `attachment; filename="${params.filename}"`,
    },
  });
}
