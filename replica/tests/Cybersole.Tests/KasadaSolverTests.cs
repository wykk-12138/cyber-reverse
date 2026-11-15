using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Cybersole.Stores.Scripts;
using Xunit;
using Xunit.Abstractions;

namespace Cybersole.Tests;

/// <summary>
/// Round 137: the four roads as code — an interface, one implementation per mode, and a runner that
/// walks them in the order the image's strings imply.
///
/// <para>
/// The runner is where the strategy lives: <c>Api</c> first (getting is cheap and the image numbers its
/// attempts), then <c>Local</c> (solving), then the two named fallbacks. When every road is empty it
/// returns the image's own give-up string with the statuses that led there, so a failure explains
/// itself.
/// </para>
///
/// <para>
/// The API address is deliberately <b>not</b> invented: the strings prove a service exists and never
/// name it, so an unconfigured <c>ApiKasadaSolver</c> reports
/// <c>Kasada API down (Contact staff)</c> — the operator message the image already has for exactly
/// that condition.
/// </para>
/// </summary>
public sealed class KasadaSolverChainTests
{
    private readonly ITestOutputHelper _out;

    public KasadaSolverChainTests(ITestOutputHelper output) => _out = output;

    private sealed class Stub : IKasadaSolver
    {
        private readonly string? _token;
        private readonly string _status;

        public Stub(KasadaStrategy.Mode mode, string? token, string? status = null)
        {
            Mode = mode;
            _token = token;
            _status = status ?? (token is null ? "failed " + mode : "ok " + mode);
        }

        public KasadaStrategy.Mode Mode { get; }

        public bool Tried { get; private set; }

        public Task<KasadaToken> GetAsync(string pageUrl, CancellationToken ct = default)
        {
            Tried = true;
            return Task.FromResult(_token is null
                ? KasadaToken.Failed(_status, Mode)
                : new KasadaToken(_token, Mode, _status));
        }
    }

    /// <summary>The default order is Api → Local → Fallback → MobileFallback.</summary>
    [Fact]
    public void TheOrderIsApiLocalFallbackMobileFallback()
    {
        var runner = KasadaStrategyRunner.Default();

        Assert.Equal(new[]
        {
            KasadaStrategy.Mode.Api, KasadaStrategy.Mode.Local,
            KasadaStrategy.Mode.Fallback, KasadaStrategy.Mode.MobileFallback,
        }, runner.Order);

        _out.WriteLine(string.Join(" → ", runner.Order));
    }

    /// <summary>The first road that produces a token wins, and later roads are not tried.</summary>
    [Fact]
    public async Task TheFirstUsableTokenWins()
    {
        var api = new Stub(KasadaStrategy.Mode.Api, null);
        var local = new Stub(KasadaStrategy.Mode.Local, "ct-token");
        var fallback = new Stub(KasadaStrategy.Mode.Fallback, "should-not-be-used");

        var runner = new KasadaStrategyRunner(new IKasadaSolver[] { api, local, fallback });
        var token = await runner.GetAsync("https://example.test");

        Assert.True(token.Usable);
        Assert.Equal("ct-token", token.Token);
        Assert.Equal(KasadaStrategy.Mode.Local, token.Mode);
        Assert.True(api.Tried);
        Assert.True(local.Tried);
        Assert.False(fallback.Tried);
    }

    /// <summary>A fallback token is usable and says which fallback it came from.</summary>
    [Fact]
    public async Task AFallbackTokenCarriesItsOwnName()
    {
        var local = new NamedFallbackSolver(KasadaStrategy.Mode.MobileFallback,
            (_, _) => Task.FromResult<string?>("mobile-token"));

        var token = await local.GetAsync("https://example.test");

        Assert.True(token.Usable);
        Assert.Equal("mobile-token", token.Token);
        Assert.Equal(KasadaStrategy.MobileFallback, token.Status);
    }

    /// <summary>Every road empty → the image's give-up string, with the statuses that led there.</summary>
    [Fact]
    public async Task EveryRoadEmptyGivesUpWithTheImagesString()
    {
        var runner = new KasadaStrategyRunner(new IKasadaSolver[]
        {
            new Stub(KasadaStrategy.Mode.Api, null, "Failed getting Kasada"),
            new Stub(KasadaStrategy.Mode.Local, null, "Failed solving Kasada (TL)"),
            new NamedFallbackSolver(KasadaStrategy.Mode.Fallback),
            new NamedFallbackSolver(KasadaStrategy.Mode.MobileFallback),
        });

        var token = await runner.GetAsync("https://example.test");

        Assert.False(token.Usable);
        Assert.Equal("Failed Kasada (Retry limit reached)", KasadaStrategyRunner.GaveUpStatus);
        Assert.Contains(KasadaStrategyRunner.GaveUpStatus, token.Status);
        Assert.Contains("Failed getting Kasada", token.Status);
        Assert.Contains("Failed solving Kasada (TL)", token.Status);
        Assert.Contains(KasadaStrategy.Fallback, token.Status);

        _out.WriteLine(token.Status);
    }

    /// <summary>An unconfigured API reports the operator message instead of inventing a host.</summary>
    [Fact]
    public async Task TheApiRoadWithoutAnAddressSaysSo()
    {
        var solver = new ApiKasadaSolver();

        Assert.False(solver.IsConfigured);

        var token = await solver.GetAsync("https://example.test");
        Assert.False(token.Usable);
        Assert.Equal("Kasada API down (Contact staff)", token.Status);
    }

    /// <summary>A configured API with a working call produces an api-mode token.</summary>
    [Fact]
    public async Task AConfiguredApiProducesAnApiToken()
    {
        var solver = new ApiKasadaSolver("https://solver.test/kasada",
            (_, _, _) => Task.FromResult<string?>("api-token"));

        Assert.True(solver.IsConfigured);

        var token = await solver.GetAsync("https://example.test");

        Assert.True(token.Usable);
        Assert.Equal(KasadaStrategy.Mode.Api, token.Mode);
        Assert.Equal("api-token", token.Token);
        Assert.StartsWith("Getting Kasada", token.Status, StringComparison.Ordinal);
    }

    /// <summary>Only the two fallback modes may be named fallbacks.</summary>
    [Fact]
    public void AFallbackCannotClaimAnotherMode()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            new NamedFallbackSolver(KasadaStrategy.Mode.Api));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            new NamedFallbackSolver(KasadaStrategy.Mode.Local));

        Assert.Equal(KasadaStrategy.Fallback,
            new NamedFallbackSolver(KasadaStrategy.Mode.Fallback).StatusName);
        Assert.Equal(KasadaStrategy.MobileFallback,
            new NamedFallbackSolver(KasadaStrategy.Mode.MobileFallback).StatusName);
    }

    /// <summary>Every implementation answers for exactly one mode, and they cover all four.</summary>
    [Fact]
    public void TheImplementationsCoverEveryMode()
    {
        var modes = new List<KasadaStrategy.Mode>
        {
            new ApiKasadaSolver().Mode,
            new LocalKasadaSolver().Mode,
            new NamedFallbackSolver(KasadaStrategy.Mode.Fallback).Mode,
            new NamedFallbackSolver(KasadaStrategy.Mode.MobileFallback).Mode,
        };

        Assert.Equal(4, modes.Count);
        Assert.Equal(4, new HashSet<KasadaStrategy.Mode>(modes).Count);

        foreach (var mode in modes) _out.WriteLine(mode.ToString());
    }
}
