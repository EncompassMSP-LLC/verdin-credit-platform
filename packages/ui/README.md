# @verdin/ui

Reusable UI components for the Verdin Credit Platform design system. Built with React, TypeScript, and Tailwind CSS utility classes.

## Conventions

| Rule              | Detail                                                                  |
| ----------------- | ----------------------------------------------------------------------- |
| **Naming**        | PascalCase components (`Button`, `PageHeader`); `*Props` for prop types |
| **Styling**       | Tailwind classes via `className`; use `cn()` to merge overrides         |
| **Scope**         | Generic, domain-agnostic primitives only — no business logic            |
| **Accessibility** | Labels, ARIA roles, keyboard support, and focus styles where applicable |
| **Forms**         | `forwardRef` on inputs for React Hook Form compatibility                |

## Installation

This package is a workspace dependency:

```json
{
  "dependencies": {
    "@verdin/ui": "workspace:*"
  }
}
```

Ensure `tailwind.config.js` scans the UI package:

```js
content: ['../../packages/ui/src/**/*.{js,ts,jsx,tsx}'],
```

## Usage examples

### Button

```tsx
import { Button } from '@verdin/ui';

<Button variant="primary" size="md" loading={isSubmitting}>
  Save
</Button>;
```

### Card (compound)

```tsx
import { Card, CardContent, CardHeader, CardTitle } from '@verdin/ui';

<Card>
  <CardHeader>
    <CardTitle>Overview</CardTitle>
  </CardHeader>
  <CardContent>
    <p className="text-sm text-gray-500">Content goes here.</p>
  </CardContent>
</Card>;
```

### Form field

```tsx
import { FormField, Input } from '@verdin/ui';

<FormField label="Email" htmlFor="email" error={errors.email?.message} required>
  <Input id="email" type="email" hasError={!!errors.email} {...register('email')} />
</FormField>;
```

### Page header + stat cards

```tsx
import { PageHeader, StatCard } from '@verdin/ui';

<PageHeader title="Dashboard" description="Overview of your workspace." />
<div className="mt-8 grid grid-cols-4 gap-6">
  <StatCard label="Total" value="128" />
</div>;
```

### Table

```tsx
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@verdin/ui';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Item</TableCell>
      <TableCell>Active</TableCell>
    </TableRow>
  </TableBody>
</Table>;
```

### Dialog

```tsx
import { Dialog } from '@verdin/ui';

<Dialog open={open} onClose={() => setOpen(false)} title="Confirm" description="Are you sure?">
  <p className="text-sm text-gray-600">This action cannot be undone.</p>
</Dialog>;
```

### Tabs

```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@verdin/ui';

<Tabs defaultValue="tab-a">
  <TabsList>
    <TabsTrigger value="tab-a">Tab A</TabsTrigger>
    <TabsTrigger value="tab-b">Tab B</TabsTrigger>
  </TabsList>
  <TabsContent value="tab-a">Panel A</TabsContent>
  <TabsContent value="tab-b">Panel B</TabsContent>
</Tabs>;
```

### Layout shell

```tsx
import { AppShell, Main, ShellContent, Sidebar } from '@verdin/ui';

<AppShell>
  <Sidebar className="bg-brand-900 text-white">{/* navigation */}</Sidebar>
  <Main>
    <ShellContent>{/* page content */}</ShellContent>
  </Main>
</AppShell>;
```

### States

```tsx
import { EmptyState, ErrorState, LoadingState, StatusChip } from '@verdin/ui';

<LoadingState message="Fetching data..." />
<EmptyState title="No results" description="Try adjusting your filters." />
<ErrorState message="Unable to load data." />
<StatusChip variant="success">Active</StatusChip>;
```

## Component index

| Component                                     | Purpose                              |
| --------------------------------------------- | ------------------------------------ |
| `Button`                                      | Actions and form submission          |
| `Card`                                        | Grouped content container            |
| `Input`, `Textarea`, `Select`                 | Form controls                        |
| `Label`, `FormField`                          | Accessible field labels and wrappers |
| `Badge`, `StatusChip`                         | Compact status indicators            |
| `Table`                                       | Tabular data display                 |
| `Dialog` / `Modal`                            | Overlay panels                       |
| `Tabs`                                        | Tabbed content                       |
| `PageHeader`                                  | Page title and actions               |
| `StatCard`                                    | Metric highlight card                |
| `EmptyState`, `LoadingState`, `ErrorState`    | Feedback states                      |
| `AppShell`, `Sidebar`, `Main`, `ShellContent` | Layout primitives                    |

## Development

```bash
pnpm --filter @verdin/ui build
pnpm --filter @verdin/ui lint
pnpm --filter @verdin/ui typecheck
```
