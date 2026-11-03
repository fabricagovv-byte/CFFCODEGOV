var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/api/health", () => Results.Ok(new { status = "ok", sistema = "{{NOME}}" }));
app.Run();

public partial class Program { }
