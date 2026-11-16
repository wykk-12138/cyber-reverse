using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;

namespace Cybersole.Ui.Views;

/// <summary>
/// Simple bar chart drawn with a <see cref="Canvas"/> — no charting dependency.
/// Renders per-store checkout counts (success vs failed) from <c>Cybersole.Services.CheckoutStats</c>.
/// </summary>
public sealed class StoreBarChart : Control
{
    private IReadOnlyDictionary<string, (int Success, int Failed)> _data =
        new Dictionary<string, (int, int)>();

    private static readonly IBrush SuccessBrush = new SolidColorBrush(Color.Parse("#2EA043"));
    private static readonly IBrush FailedBrush = new SolidColorBrush(Color.Parse("#F85149"));
    private static readonly IBrush LabelBrush = new SolidColorBrush(Color.Parse("#C9D1D9"));
    private static readonly IBrush AxisBrush = new SolidColorBrush(Color.Parse("#30363D"));

    private IReadOnlyList<(DateTimeOffset From, DateTimeOffset To, int Total, int Success)>? _timeline;

    public void Update(IReadOnlyDictionary<string, (int Success, int Failed)> data)
    {
        _data = data;
        _timeline = null;
        InvalidateVisual();
    }

    /// <summary>
    /// Switch the chart to a time series (Cybersole.Services.CheckoutStats.Buckets).
    /// Buckets arrive newest-first; the chart draws them oldest-first so time flows right.
    /// </summary>
    public void UpdateTimeline(
        IReadOnlyList<(DateTimeOffset From, DateTimeOffset To, int Total, int Success)> buckets)
    {
        _timeline = buckets;
        InvalidateVisual();
    }

    /// <summary>True when the chart is currently showing a timeline rather than per-store bars.</summary>
    public bool IsTimeline => _timeline is not null;

    public override void Render(DrawingContext context)
    {
        base.Render(context);

        var width = Bounds.Width;
        var height = Bounds.Height;
        if (width <= 0 || height <= 0) return;

        // axis
        context.DrawLine(new Pen(AxisBrush, 1),
            new Point(36, height - 24), new Point(width - 8, height - 24));

        if (_timeline is not null)
        {
            RenderTimeline(context, width, height);
            return;
        }

        var entries = _data
            .OrderByDescending(kv => kv.Value.Success + kv.Value.Failed)
            .Take(12)
            .ToList();

        if (entries.Count == 0)
        {
            context.DrawText(
                new FormattedText("No checkouts yet", System.Globalization.CultureInfo.InvariantCulture,
                    FlowDirection.LeftToRight, Typeface.Default, 12, LabelBrush),
                new Point(12, height / 2 - 8));
            return;
        }

        var max = Math.Max(1, entries.Max(e => e.Value.Success + e.Value.Failed));
        var chartWidth = width - 48 - 8;
        var barSlot = chartWidth / entries.Count;
        var barWidth = Math.Min(40, barSlot * 0.6);

        for (var i = 0; i < entries.Count; i++)
        {
            var (store, counts) = (entries[i].Key, entries[i].Value);
            var total = counts.Success + counts.Failed;
            var barHeight = (height - 60) * total / max;

            var x = 40 + i * barSlot + (barSlot - barWidth) / 2;
            var baseY = height - 24;

            // failed portion on top of success
            var successHeight = barHeight * counts.Success / Math.Max(1, total);
            var failedHeight = barHeight - successHeight;

            if (successHeight > 0)
            {
                context.FillRectangle(SuccessBrush,
                    new Rect(x, baseY - successHeight, barWidth, successHeight));
            }
            if (failedHeight > 0)
            {
                context.FillRectangle(FailedBrush,
                    new Rect(x, baseY - successHeight - failedHeight, barWidth, failedHeight));
            }

            var label = new FormattedText(store.Length > 10 ? store[..10] : store,
                System.Globalization.CultureInfo.InvariantCulture,
                FlowDirection.LeftToRight, Typeface.Default, 10, LabelBrush);
            context.DrawText(label, new Point(x + (barWidth - label.Width) / 2, baseY + 4));
        }

        DrawLegend(context);
    }

    private void RenderTimeline(DrawingContext context, double width, double height)
    {
        var buckets = _timeline!;
        if (buckets.Count == 0)
        {
            context.DrawText(
                new FormattedText("No history yet", System.Globalization.CultureInfo.InvariantCulture,
                    FlowDirection.LeftToRight, Typeface.Default, 12, LabelBrush),
                new Point(12, height / 2 - 8));
            return;
        }

        // oldest first so time runs left to right
        var ordered = buckets.OrderBy(b => b.From).ToList();
        var max = Math.Max(1, ordered.Max(b => b.Total));
        var chartWidth = width - 48 - 8;
        var slot = chartWidth / ordered.Count;
        var barWidth = Math.Min(36, slot * 0.65);
        var baseY = height - 24;
        var usable = height - 60;

        for (var i = 0; i < ordered.Count; i++)
        {
            var (from, _, total, success) = ordered[i];
            if (total <= 0)
            {
                // draw a thin tick so an empty bucket is still visible
                context.FillRectangle(AxisBrush,
                    new Rect(40 + i * slot + (slot - barWidth) / 2, baseY - 2, barWidth, 2));
                continue;
            }

            var barHeight = usable * total / max;
            var successHeight = barHeight * success / Math.Max(1, total);
            var failedHeight = barHeight - successHeight;
            var x = 40 + i * slot + (slot - barWidth) / 2;

            if (successHeight > 0)
                context.FillRectangle(SuccessBrush,
                    new Rect(x, baseY - successHeight, barWidth, successHeight));
            if (failedHeight > 0)
                context.FillRectangle(FailedBrush,
                    new Rect(x, baseY - successHeight - failedHeight, barWidth, failedHeight));

            var label = new FormattedText(from.ToString("HH:mm"),
                System.Globalization.CultureInfo.InvariantCulture,
                FlowDirection.LeftToRight, Typeface.Default, 9, LabelBrush);
            context.DrawText(label, new Point(x + (barWidth - label.Width) / 2, baseY + 4));
        }

        DrawLegend(context);
    }

    private void DrawLegend(DrawingContext context)
    {
        var ok = new FormattedText("success", System.Globalization.CultureInfo.InvariantCulture,
            FlowDirection.LeftToRight, Typeface.Default, 10, SuccessBrush);
        var bad = new FormattedText("failed", System.Globalization.CultureInfo.InvariantCulture,
            FlowDirection.LeftToRight, Typeface.Default, 10, FailedBrush);
        context.DrawText(ok, new Point(40, 4));
        context.DrawText(bad, new Point(40 + ok.Width + 16, 4));
    }
}
