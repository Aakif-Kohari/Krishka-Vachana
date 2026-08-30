# UI Design Rules — Team Standard v1.0

## Purpose

Every page must look like it belongs to the same website.

Developers must follow these UI rules instead of creating their own visual styles.

The interface should prioritize:

- Clarity
- Usability
- Consistency
- Accessibility
- Whitespace
- Professional appearance

---

## 1. Overall Design Style

Use a modern, clean, professional, minimal UI.

The interface should feel:

- Trustworthy
- Simple
- Spacious
- Easy to understand
- Professional
- Friendly

### Avoid
- Overly decorative designs.
- Excessive gradients.
- Excessive animations.
- Glowing effects.
- Heavy shadows.
- Unnecessary visual complexity.

Prioritize clarity and usability over decoration.

Maintain plenty of whitespace between sections.

All pages must follow the same visual language.

---

## 2. Color System

### Primary Brand Colors

| Token | Color |
|---|---|
| Primary Dark | `#123524` |
| Primary | `#1F6B45` |
| Primary Button | `#2E8B57` |
| Primary Light | `#DDF3E6` |
| Primary Background | `#F0FAF4` |

### Neutral Colors

| Token | Color |
|---|---|
| Main Text | `#17201B` |
| Secondary Text | `#34413A` |
| Muted Text | `#68756D` |
| Placeholder | `#AAB4AE` |
| Border | `#D1D8D3` |
| Divider | `#E5EAE7` |
| Light Background | `#F1F4F2` |
| Page Background | `#F8FAF9` |
| Card Background | `#FFFFFF` |

### Semantic Colors

| Purpose | Color | Background |
|---|---|---|
| Success | `#16803C` | `#E8F7ED` |
| Warning | `#B7791F` | `#FFF6DE` |
| Error | `#C53030` | `#FDECEC` |
| Info | `#2563EB` | `#EAF2FF` |

### Color Rules
- Do not introduce random colors.
- Do not create new shades of green for individual pages.
- Use semantic colors only for their intended purpose.
- Primary green represents primary actions and brand identity.
- Red is primarily for errors and destructive actions.
- Yellow/orange is primarily for warnings and waiting states.
- Blue is primarily for informational elements.

---

## 3. Typography

Use **Inter** throughout the entire website.

**Font fallback**
```
Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

### Allowed Font Weights

| Weight | Usage |
|---|---|
| 400 | Regular |
| 500 | Medium |
| 600 | SemiBold |
| 700 | Bold |

Do not introduce other font weights without a clear system-level requirement.

---

## 4. Typography Scale

Only use the following typography scale.

| Level | Size | Weight | Line Height |
|---|---|---|---|
| Display | 40px | 700 | 48px |
| H1 | 32px | 700 | 40px |
| H2 | 24px | 700 | 32px |
| H3 | 20px | 600 | 28px |
| H4 | 18px | 600 | 24px |
| Body Large | 18px | 400 | 28px |
| Body | 16px | 400 | 24px |
| Body Small | 14px | 400 | 20px |
| Caption | 12px | 500 | 16px |

### Typography Rules
- Do not randomly use 15px, 17px, 19px, etc.
- Use the closest predefined typography level.
- Page titles should generally use H1.
- Section titles should generally use H2/H3.
- Supporting information should use Body Small or Caption.

---

## 5. Buttons

Only use these button styles:

- Primary
- Secondary
- Ghost
- Danger

Every button must support:

- Default
- Hover
- Active
- Focus
- Disabled
- Loading

### Primary Button
- Background: `#2E8B57`
- Text: white
- Height: 44px
- Border radius: 8px
- Horizontal padding: 16px
- Font size: 14px
- Font weight: 600

Use for:
- Submit
- Continue
- Confirm
- Book Slot
- Save
- Main actions

### Secondary Button
- Background: white
- Border: 1px solid `#D1D8D3`
- Text: `#34413A`
- Height: 44px
- Radius: 8px

Use for:
- Cancel
- Back
- View Details
- Secondary actions

### Ghost Button
- Background: transparent
- Border: none
- Text: primary green
- Height: 40px

Use for low-priority actions.

### Danger Button
- Background: `#C53030`
- Text: white
- Radius: 8px

Use for:
- Delete
- Remove
- Destructive actions

---

## 6. Cards

Cards are one of the main UI elements.

### Standard Card
- Background: white
- Border: 1px solid `#E5EAE7`
- Radius: 12px
- Padding: 20px
- Shadow: Small

Use a subtle shadow only. Never use heavy shadows.

### Card Structure
```
Card
├── Header
│   ├── Title
│   └── Optional Action
├── Content
└── Optional Footer
```

Cards can be used for:
- Dashboard statistics
- Queue information
- Booking information
- Payment information
- Notifications
- Profile information
- Forms
- Summary sections

**Rule:** If two cards contain similar information, they should use the same visual structure.

---

## 7. Input Fields

All input fields must use the same input component.

### Standard Input
- Height: 44px
- Background: white
- Border: 1px solid `#D1D8D3`
- Radius: 8px
- Horizontal padding: 12px
- Font size: 14px

### Label
- Font size: 14px
- Weight: 500
- Color: `#34413A`
- Margin below: 6px

### Input States

Every input should support:
- Default
- Hover
- Focus
- Error
- Disabled
- Success

**Focus**
- Border: primary green
- Focus ring: subtle green

**Error**
- Border: error red
- Error message: displayed below input
- Error text: 12px

---

## 8. Navbar

The navbar must remain consistent across pages.

### Desktop
- Height: 64px
- Background: white
- Bottom border: 1px solid `#E5EAE7`

Typical structure:
```
┌──────────────────────────────────────────────────────┐
│ Logo     Navigation / Search       Notifications User │
└──────────────────────────────────────────────────────┘
```

Navbar may contain:
- Logo
- Navigation
- Search
- Notifications
- User profile
- Menu control

### Rules
- Do not create a different navbar for each page.
- Navbar height must remain consistent.
- Navbar icons should use the standard icon library.
- Profile controls should have consistent styling.

---

## 9. Sidebar

Use the same sidebar throughout dashboard/admin pages.

### Desktop
- Width: 240px
- Background: white
- Right border: 1px solid `#E5EAE7`

### Navigation Item
- Height: 44px
- Horizontal padding: 12px
- Radius: 8px

Structure: `Icon + Text`

Maintain consistent spacing.

### Active Item
- Background: `#DDF3E6`
- Text: primary dark
- Icon: primary green

An optional left indicator may be used.

### Rules
- Do not create different sidebar designs for different dashboard pages.
- Navigation order should remain consistent.
- On mobile, convert the sidebar into a drawer.

---

## 10. Icons

Use **Lucide Icons** throughout the application.

Do not mix multiple icon libraries.

### Sizes

| Size | Usage |
|---|---|
| Small | 16px |
| Default | 20px |
| Large | 24px |

### Style
- Use consistent stroke-based icons.
- Default stroke width should be approximately 2px.
- Icons should support the meaning of content.
- Icons should not replace important text when text is required for clarity.

### Standard Icons

| Meaning | Icon |
|---|---|
| Dashboard | `LayoutDashboard` |
| Home | `House` |
| Booking | `CalendarCheck` |
| Queue | `Users` |
| Payment | `CreditCard` |
| Notifications | `Bell` |
| Settings | `Settings` |
| Search | `Search` |
| Edit | `Pencil` |
| Delete | `Trash2` |

---

## 11. Modals

### Standard Modal
- Background: white
- Radius: 16px
- Padding: 24px
- Maximum width: approximately 480px
- Shadow: Large

### Structure
```
Title                              X

Description / Content

Optional Form

                       Cancel    Confirm
```

### Rules
- Always provide a close/cancel option.
- Destructive actions require confirmation.
- Do not create a completely different modal design for individual pages.
- Keep modal content concise.

---

## 12. Tables

Use tables for structured information.

### Table
- Header height: 44px
- Row height: approximately 56px
- Font size: 14px
- Horizontal padding: 12–16px
- Background: white
- Bottom borders: `#E5EAE7`

### Table Header
- Background: `#F8FAF9`
- Font weight: 600

### Status
Use standard status badges instead of random colors.

### Mobile
Do not squeeze large tables into mobile screens.

Use one of:
- Horizontal scrolling
- Responsive card layout
- Condensed table when appropriate

---

## 13. Status Badges

Use consistent badges everywhere.

| Status | Background | Text |
|---|---|---|
| Confirmed | `#E8F7ED` | `#16803C` |
| Waiting | `#FFF6DE` | `#B7791F` |
| Processing | `#EAF2FF` | `#2563EB` |
| Cancelled | `#FDECEC` | `#C53030` |
| Completed | `#DDF3E6` | `#174A32` |

### Badge Styling
- Border radius: 9999px
- Font size: 12–14px
- Font weight: 500
- Comfortable horizontal padding

---

## 14. Spacing

Use a 4px spacing system.

### Allowed Primary Values
`4px` `8px` `12px` `16px` `20px` `24px` `32px` `40px` `48px` `64px` `80px`

### Common Usage

| Usage | Spacing |
|---|---|
| Icon ↔ text | 4–8px |
| Small element spacing | 8px |
| Input padding | 12px |
| Component spacing | 16px |
| Card padding | 20px |
| Section spacing | 24–32px |
| Major section spacing | 48px+ |

**Important:** Do not randomly use `13px`, `17px`, `19px`, `23px`, `27px`, `31px`. Use the nearest value from the spacing system.

---

## 15. Border Radius

Only use:

| Radius | Usage |
|---|---|
| 4px | Small elements |
| 8px | Buttons / Inputs |
| 12px | Cards |
| 16px | Modals / Large containers |
| 9999px | Pills / Badges / Avatars |

Do not randomly introduce new radius values.

---

## 16. Shadows

Keep shadows subtle.

### Small
```
0 1px 2px rgba(0, 0, 0, 0.05)
```
Use for cards.

### Medium
```
0 4px 12px rgba(0, 0, 0, 0.08)
```
Use for:
- Dropdowns
- Floating elements

### Large
```
0 10px 30px rgba(0, 0, 0, 0.12)
```
Use for modals.

**Rule:** Avoid heavy shadows everywhere. The interface should feel clean and lightweight.

---

## 17. Page Layout

### Standard Dashboard Layout
```
┌──────────────────────────────────────────────┐
│                   NAVBAR                     │
├───────────────┬──────────────────────────────┤
│               │                              │
│               │       PAGE CONTENT           │
│   SIDEBAR     │                              │
│               │                              │
│               │                              │
└───────────────┴──────────────────────────────┘
```

### Desktop
- Maximum width: 1280px
- Page padding: approximately 24px

Center content where appropriate.

### Mobile
- Page padding: approximately 16px

### Rules
- Do not make content touch the screen edges.
- Maintain consistent page margins.
- Keep related content grouped together.
- Use whitespace to separate sections.

---

## 18. Responsive Breakpoints

Use the same breakpoints throughout the entire project.

| Breakpoint | Range |
|---|---|
| Small Mobile | < 480px |
| Mobile | 480–767px |
| Tablet | 768–1023px |
| Desktop | 1024–1279px |
| Large Desktop | 1280px+ |

---

## 19. Responsive Behavior

Do not design desktop first and simply shrink it.

Each page must intentionally adapt across: **Mobile → Tablet → Desktop**

### Mobile
- Sidebar → Drawer
- Navbar → Hamburger/menu
- Cards → Single column
- Multi-column sections → Single column
- Tables → Horizontal scroll/cards
- Buttons → Touch-friendly
- Reduce unnecessary decorative elements

### Tablet
- Sidebar can collapse.
- Use 2-column layouts where appropriate.
- Maintain comfortable spacing.

### Desktop
- Full sidebar.
- Multi-column dashboard layouts.
- Maximum content width: 1280px.

### Responsive Checklist

Check:
- Text wrapping
- Card stacking
- Navigation
- Tables
- Buttons
- Forms
- Images
- Spacing
- Sidebar
- Modals

---

## 20. Loading States

Never show a completely blank page while content is loading.

Use:
- Skeleton loaders
- Button loading states
- Spinners where appropriate

Loading states should preserve the page structure whenever possible.

---

## 21. Empty States

Every list and table should have an empty state.

Example:
```
No bookings yet

You haven't booked a procurement slot.

             [Book a Slot]
```

Empty states should be:
- Simple
- Friendly
- Clear
- Action-oriented

---

## 22. Error States

Every important section should have an error state.

Example:
```
Something went wrong

We couldn't load your information.

             [Try Again]
```

Do not simply display:
```
ERROR 500
```
to the user.

Errors should explain what happened and, where possible, provide a recovery action.

---

## 23. Accessibility

Every developer must follow basic accessibility rules.

### Required
- Inputs must have labels.
- Buttons must be keyboard accessible.
- Focus states must be visible.
- Icons used as buttons need accessible labels.
- Do not use color alone to communicate status.
- Maintain sufficient text/background contrast.
- Touch targets should generally be around 44px or larger.
- Interactive elements must have clear hover and focus states.

---

## 24. Design Consistency Rules

Before creating a new UI pattern, check whether an existing component already solves the problem.

### Prefer
- Shared Button
- Shared Input
- Shared Card
- Shared Modal
- Shared Badge
- Shared Table
- Shared Navbar
- Shared Sidebar

### Avoid
- Custom button on one page
- Custom card on another page
- Custom badge colors
- Custom navbar
- Custom sidebar
- Random spacing
- Random font sizes
- Random border radii

The goal is for users to feel that every page belongs to the same product.

---

## 25. Developer Checklist

Before considering a page complete, verify:

- [ ] Uses the approved color system.
- [ ] Uses Inter typography.
- [ ] Uses approved font sizes and weights.
- [ ] Uses the standard spacing system.
- [ ] Uses approved border radii.
- [ ] Uses approved shadows.
- [ ] Uses shared UI components.
- [ ] Uses Lucide icons.
- [ ] Includes loading states.
- [ ] Includes empty states where applicable.
- [ ] Includes error states where applicable.
- [ ] Works on mobile.
- [ ] Works on tablet.
- [ ] Works on desktop.
- [ ] Has visible focus states.
- [ ] Has accessible labels.
- [ ] Does not rely on color alone for status.
- [ ] Does not introduce arbitrary visual styles.

---

## 26. Source of Truth

`UI_rules.md` is the source of truth for visual design.

`frontend_architecture.md` is the source of truth for frontend structure and organization.

When implementing a new page:

```
Architecture
    ↓
Reusable Components
    ↓
Shared Design Tokens
    ↓
Page Implementation
    ↓
Responsive + Accessibility Review
```

Any deviation from these standards should have a clear technical or product reason.
