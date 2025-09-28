import reflex as rx
from app.state import CurrencyState


def currency_selector(
    label: str, value: rx.Var[str], on_change: rx.event.EventHandler
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="text-sm font-medium text-gray-700"),
        rx.el.select(
            rx.foreach(
                CurrencyState.currencies,
                lambda currency: rx.el.option(currency, value=currency),
            ),
            value=value,
            on_change=on_change,
            class_name="w-full mt-1 p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500",
        ),
        class_name="w-full",
    )


def results_table() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2("Results", class_name="text-2xl font-bold text-gray-800 mb-4"),
            rx.cond(
                CurrencyState.results.length() > 0,
                rx.el.button(
                    "Download CSV",
                    rx.icon("download", class_name="ml-2"),
                    on_click=CurrencyState.download_csv,
                    class_name="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center",
                ),
            ),
            class_name="flex justify-between items-center",
        ),
        rx.el.div(
            rx.cond(
                CurrencyState.is_loading,
                rx.el.div(
                    rx.spinner(size="3"),
                    class_name="flex justify-center items-center p-8 border-2 border-dashed border-gray-300 rounded-lg h-48 animate-pulse",
                ),
                rx.cond(
                    CurrencyState.results.length() > 0,
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Date",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Exchange Rate",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(
                                CurrencyState.results,
                                lambda item: rx.el.tr(
                                    rx.el.td(
                                        item["date"],
                                        class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-800",
                                    ),
                                    rx.el.td(
                                        item["rate"],
                                        class_name="px-6 py-4 whitespace-nowrap text-sm font-semibold text-indigo-600",
                                    ),
                                    class_name="border-b border-gray-200 hover:bg-gray-50",
                                ),
                            ),
                            class_name="bg-white divide-y divide-gray-200",
                        ),
                        class_name="min-w-full divide-y divide-gray-200 shadow rounded-lg",
                    ),
                    rx.el.div(
                        rx.cond(
                            CurrencyState.error_message != "",
                            rx.el.p(
                                CurrencyState.error_message, class_name="text-red-500"
                            ),
                            rx.el.p(
                                "Results will be displayed here.",
                                class_name="text-gray-500",
                            ),
                        ),
                        class_name="text-center p-8 border-2 border-dashed border-gray-300 rounded-lg",
                    ),
                ),
            ),
            class_name="mt-4",
        ),
        class_name="w-full max-w-4xl mx-auto mt-12",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "FX Rate Finder",
                    class_name="text-4xl font-extrabold text-gray-900 tracking-tight",
                ),
                rx.el.p(
                    "Get historical exchange rates quickly.",
                    class_name="mt-2 text-lg text-gray-600",
                ),
                class_name="text-center mb-10",
            ),
            rx.el.div(
                rx.el.div(
                    currency_selector(
                        "From Currency",
                        CurrencyState.from_currency,
                        CurrencyState.set_from_currency,
                    ),
                    currency_selector(
                        "To Currency",
                        CurrencyState.to_currency,
                        CurrencyState.set_to_currency,
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6",
                ),
                rx.el.label(
                    "Paste dates (one per line)",
                    class_name="block text-sm font-medium text-gray-700 mb-2",
                ),
                rx.el.textarea(
                    placeholder="""YYYY-MM-DD
2023-12-24
2024-01-01""",
                    on_change=CurrencyState.set_dates_input,
                    class_name="w-full h-32 p-3 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500",
                ),
                rx.el.button(
                    rx.cond(
                        CurrencyState.is_loading,
                        rx.spinner(color="white", size="2"),
                        rx.el.span("Get FX Rates"),
                    ),
                    on_click=CurrencyState.get_fx_rates,
                    disabled=CurrencyState.is_loading,
                    class_name="w-full mt-6 py-3 px-4 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center",
                ),
                class_name="w-full max-w-4xl mx-auto p-8 bg-white rounded-xl shadow-lg border border-gray-200",
            ),
            results_table(),
            rx.el.div(
                rx.el.p(
                    "Powered by the ",
                    rx.el.a(
                        "Frankfurter API",
                        href="https://www.frankfurter.app/",
                        target="_blank",
                        class_name="text-indigo-600 hover:underline",
                    ),
                    ".",
                    class_name="text-sm text-gray-500 mt-12 text-center",
                )
            ),
            class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12",
        ),
        on_mount=CurrencyState.on_load,
        class_name="font-['Poppins'] bg-gray-50 min-h-screen",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, title="FX Rate Finder")