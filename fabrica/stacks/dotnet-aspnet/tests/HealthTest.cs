using Microsoft.AspNetCore.Mvc.Testing;

public class HealthTest : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _cliente;
    public HealthTest(WebApplicationFactory<Program> f) => _cliente = f.CreateClient();

    [Fact]
    public async Task HealthRespondeOk()
    {
        var r = await _cliente.GetAsync("/api/health");
        r.EnsureSuccessStatusCode();
        Assert.Contains("\"ok\"", await r.Content.ReadAsStringAsync());
    }
}
