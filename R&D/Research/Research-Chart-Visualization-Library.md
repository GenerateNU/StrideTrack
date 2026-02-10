# Chart Visualization Library Research


## What We Need

A library to create charts that show:
- **Performance over time**
- **Athlete comparisons**
The library must work with our current technology (React, TypeScript, Tailwind CSS).

---

## Top 3 Options

### 1. **Recharts**
A charting library designed specifically for React applications.

**Pros:**
- Works perfectly with our React setup
- Includes all the type checking benefits of TypeScript
- Easy to style with Tailwind (our CSS framework)
- Well documented with lots of examples online
- Smaller file size = faster page loads

**Cons:**
- Need to wrap charts in a "ResponsiveContainer" to make them resize properly
- Only creates SVG graphics (XML-based, text-file format used to describe two-dimensional vector images) (performance declines with high detials/complex graphis)

---

### 2. **Tremor**
A collection of pre built dashboard components.

**Pros:**
- Beautiful designs by default
- Built specifically for Tailwind CSS
- Includes bonus components (cards, tables, etc.) for free
- Copy-paste approach means you own all the code

**Cons:**
- Still in "beta" for React 19 (our version)
- Less flexible if you need something custom
- Larger file size than Recharts

---

### 3. **ApexCharts**
A powerful, feature-rich charting library. Has every tool imaginable but might be too much.

**Pros:**
- 30+ different chart types
- Built-in zoom, pan, and export features
- Looks professional with smooth animations

**Cons:**
- Designed for general JavaScript, then adapted for React (feels less natural)
- Harder to style with Tailwind
- Larger file size = slower page loads
- Steeper learning curve

---

## Side-by-Side Comparison

| Feature | Recharts | Tremor | ApexCharts |
|---------|:--------:|:------:|:----------:|
| **Works with React 19?** | ✅ Yes | ⚠️ Beta only | ✅ Yes |
| **TypeScript support?** | ✅ Excellent | ✅ Excellent | ✅ Good |
| **Works with Tailwind?** | ✅ Easy | ✅ Perfect | ⚠️ Manual work |
| **File Size** | Small (100KB) | Medium (120KB) | Large (150KB) |
| **Easy to Learn?** | ✅ Yes | ✅ Yes | ⚠️ Medium |
| **Time series charts?** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Comparison charts?** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Community Support** | ✅ Large | Growing | ✅ Large |
| **Open Source License** | ✅ Free (MIT) | ✅ Free (Apache) | ⚠️ Mixed |

---

## Final Recommendation: **Recharts**

Why:

1. **Best fit for our tech stack** - Designed for React from the ground up
2. **Stable and reliable** - Fully supports React 19 (not beta like Tremor)
3. **Faster load times** - Smallest file size means faster app performance
4. **Easy to customize** - Can style charts to match our design
5. **Strong community** - Lots of examples and help online
6. **Does everything we need** - Perfect for performance trends and athlete comparisons

**To keep in mind:**
- Need to add one extra line of code (ResponsiveContainer) to make charts responsive - not a big hassle

---

## Implementation Plan


**Install and Setup** 
   - Install Recharts library via npm
   - Create reusable chart components (TimeSeriesChart for performance trends, ComparisonChart for athlete vs. athlete)
   - Set up color scheme and default styling with Tailwind

**Backend Integration**
   - Connect charts to FastAPI backend using existing TanStack Query hooks
   - Wire up Orval-generated API types to chart components
   - Add loading states and error handling

