import 'package:flutter/material.dart';

void main() => runApp(const KhoeboApp());

class KhoeboApp extends StatelessWidget {
  const KhoeboApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KHOEBO DIGITAL BANKING',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xffee6c4d), brightness: Brightness.light),
        scaffoldBackgroundColor: const Color(0xfff5f4ef),
        fontFamily: 'Georgia',
        useMaterial3: true,
      ),
      home: const MobileHome(),
    );
  }
}

class MobileHome extends StatefulWidget {
  const MobileHome({super.key});

  @override
  State<MobileHome> createState() => _MobileHomeState();
}

class _MobileHomeState extends State<MobileHome> {
  int selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('KHOEBO', style: TextStyle(fontWeight: FontWeight.w700, letterSpacing: 1.4)),
        actions: [IconButton(onPressed: () {}, icon: const Icon(Icons.notifications_none))],
      ),
      body: SafeArea(child: IndexedStack(index: selectedIndex, children: const [OverviewTab(), ActivityTab(), ServicesTab()])),
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        onDestinationSelected: (index) => setState(() => selectedIndex = index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.account_balance_outlined), label: 'Overview'),
          NavigationDestination(icon: Icon(Icons.receipt_long_outlined), label: 'Activity'),
          NavigationDestination(icon: Icon(Icons.grid_view_outlined), label: 'Services'),
        ],
      ),
    );
  }
}

class OverviewTab extends StatelessWidget {
  const OverviewTab({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(padding: const EdgeInsets.all(20), children: [
      const Text('Good morning, Khotso.', style: TextStyle(fontSize: 16, color: Color(0xff64757a))),
      const SizedBox(height: 10),
      const Text('R 24,680.00', style: TextStyle(fontSize: 42, fontWeight: FontWeight.w400)),
      const Text('Available balance · Everyday account', style: TextStyle(color: Color(0xff64757a))),
      const SizedBox(height: 26),
      Row(children: [
        Expanded(child: _QuickAction(icon: Icons.north_east, label: 'Pay', onTap: () {})),
        Expanded(child: _QuickAction(icon: Icons.send_outlined, label: 'Send', onTap: () {})),
        Expanded(child: _QuickAction(icon: Icons.credit_card_outlined, label: 'Cards', onTap: () {})),
        Expanded(child: _QuickAction(icon: Icons.local_atm_outlined, label: 'ATM', onTap: () {})),
      ]),
      const SizedBox(height: 28),
      const _SectionTitle(title: 'Your money'),
      const _MobileTile(title: 'Savings pockets', detail: '2 active · R 5,050.00 saved', icon: Icons.savings_outlined),
      const _MobileTile(title: 'Rewards', detail: '1,240 points ready to use', icon: Icons.stars_outlined),
      const _MobileTile(title: 'Global money', detail: 'USD, EUR, and GBP wallets', icon: Icons.public_outlined),
      const SizedBox(height: 20),
      const _SectionTitle(title: 'Recent activity'),
      const _MobileTile(title: 'Salary received', detail: 'Today · + R 18,500.00', icon: Icons.arrow_downward, positive: true),
      const _MobileTile(title: 'Card purchase', detail: 'Yesterday · - R 420.00', icon: Icons.shopping_bag_outlined),
    ]);
  }
}

class ActivityTab extends StatelessWidget {
  const ActivityTab({super.key});

  @override
  Widget build(BuildContext context) => const Center(child: Text('Transaction history connects to banka-api'));
}

class ServicesTab extends StatelessWidget {
  const ServicesTab({super.key});

  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(20), children: const [
    _MobileTile(title: 'Payments', detail: 'Instant, scheduled, and beneficiary payments', icon: Icons.payments_outlined),
    _MobileTile(title: 'Forex', detail: 'Convert currency and submit BOP declarations', icon: Icons.currency_exchange),
    _MobileTile(title: 'ATM services', detail: 'Cardless cash and deposits', icon: Icons.local_atm_outlined),
    _MobileTile(title: 'Security centre', detail: 'Biometrics, card controls, and fraud support', icon: Icons.shield_outlined),
  ]);
}

class _QuickAction extends StatelessWidget {
  const _QuickAction({required this.icon, required this.label, required this.onTap});
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => InkWell(onTap: onTap, child: Column(children: [CircleAvatar(backgroundColor: const Color(0xff15252a), foregroundColor: Colors.white, child: Icon(icon)), const SizedBox(height: 8), Text(label)]));
}

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title});
  final String title;
  @override
  Widget build(BuildContext context) => Padding(padding: const EdgeInsets.only(bottom: 8), child: Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600)));
}

class _MobileTile extends StatelessWidget {
  const _MobileTile({required this.title, required this.detail, required this.icon, this.positive = false});
  final String title;
  final String detail;
  final IconData icon;
  final bool positive;
  @override
  Widget build(BuildContext context) => Card(margin: const EdgeInsets.only(bottom: 10), child: ListTile(leading: Icon(icon, color: positive ? const Color(0xff32875b) : const Color(0xffee6c4d)), title: Text(title), subtitle: Text(detail), trailing: const Icon(Icons.chevron_right)));
}
