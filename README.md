# AirboxVIP Coffeenet — کافینت ایرباکس وی آی پی

پروژه کافینت دیجیتال و سامانه جامع مدیریت ووچر و خدمات وای‌فای ایرباکس وی آی پی (AirboxVIP Coffeenet).

- **وب‌سایت رسمی:** [coffeenet.airboxvip.top](https://coffeenet.airboxvip.top)
- **ربات تلگرام:** [telegram_bot/](telegram_bot/)
- **عنوان رسمی فارسی:** کافینت ایرباکس وی آی پی
- **استک فنی:** Vite + React + TypeScript + Python + SQLite

---

## Technical Stack & Frontend Template

This project includes a React + TypeScript + Vite web application with Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

### React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

### Expanding the Oxlint configuration

If you are developing a production application, we recommend enabling type-aware lint rules by installing `oxlint-tsgolint` and editing `.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "typescript", "oxc"],
  "options": {
    "typeAware": true
  },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

See the [Oxlint rules documentation](https://oxc.rs/docs/guide/usage/linter/rules) for the full list of rules and categories.

