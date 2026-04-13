# Tailwind UI Agent - Design Patterns

## Modern Card Component
A clean card with soft shadows, subtle borders, and interactive hover effects.

```tsx
<div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md border border-gray-100 dark:border-gray-700 p-6 transition-all duration-300 group">
  <div className="mb-4">
    <span className="p-3 bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-lg inline-block group-hover:scale-110 transition-transform">
      {/* Icon */}
    </span>
  </div>
  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Title</h3>
  <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed">Description goes here.</p>
</div>
```

## Glassmorphism Background
For a modern, layered feel.

```tsx
<div className="bg-white/70 dark:bg-gray-900/70 backdrop-blur-md border border-white/20 dark:border-gray-800/30 rounded-2xl p-8 shadow-xl">
  {/* Content */}
</div>
```

## Responsive Grid Layout
Optimized for mobile, tablet, and desktop.

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
  {/* Grid Items */}
</div>
```

## Gradient Text
For high-impact headings.

```tsx
<h1 className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-indigo-600 dark:from-primary-400 dark:to-indigo-400">
  Visual Impact
</h1>
```

## Interactive Form Input
With focus states and validation styles.

```tsx
<div className="space-y-1">
  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Email Address</label>
  <input 
    type="email" 
    className="w-full px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all placeholder-gray-400 dark:placeholder-gray-500 text-gray-900 dark:text-white"
    placeholder="you@example.com"
  />
</div>
```
