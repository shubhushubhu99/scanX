from core.live_inspector import inspect_site

data = inspect_site("amazon.com")

print("DNS resolves:", data["dns_resolves"])
print("Homepage:", data["homepage"])
print("Signals:", data["signals"])
print("Support emails:", data["support_emails"][:2])
