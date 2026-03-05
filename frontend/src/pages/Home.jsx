import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { QrCode, Calendar, CheckCircle, ArrowRight } from 'lucide-react';

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="flex-1">
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20 sm:pt-24 sm:pb-28">
        <div className="max-w-2xl">
          <p className="text-accent font-semibold text-sm tracking-wide uppercase mb-4">Secure Event Ticketing</p>
          <h1 className="text-4xl sm:text-5xl font-bold text-text leading-[1.1] mb-5 tracking-tight">
            QR tickets that<br />can't be forged.
          </h1>
          <p className="text-lg text-text-mid leading-relaxed mb-8 max-w-lg">
            Rakshan uses cryptographic signing to make every ticket tamper-proof. Register for events, get your QR code, scan at the door.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/events" className="inline-flex items-center gap-2 bg-primary hover:bg-primary-dark text-white font-medium px-5 py-2.5 rounded-md text-sm no-underline transition-colors">
              Browse events <ArrowRight className="w-4 h-4" />
            </Link>
            {!user && (
              <Link to="/register" className="inline-flex items-center gap-2 bg-white hover:bg-surface-alt text-text font-medium px-5 py-2.5 rounded-md text-sm no-underline border border-border transition-colors">
                Create account
              </Link>
            )}
          </div>
        </div>
      </section>

      <section className="border-t border-border-light">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <p className="text-xs font-semibold text-text-muted uppercase tracking-widest mb-8">How it works</p>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Calendar, num: '01', title: 'Find & register', desc: 'Browse upcoming events and register with one click. No paperwork, no waiting.' },
              { icon: QrCode, num: '02', title: 'Get your QR ticket', desc: 'Receive a cryptographically signed QR code. Each ticket is unique and verifiable.' },
              { icon: CheckCircle, num: '03', title: 'Scan & enter', desc: 'Show your code at the venue. Instant validation, no duplicates, no fakes.' },
            ].map(({ icon: Icon, num, title, desc }) => (
              <div key={num} className="group">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-xs font-mono text-text-muted">{num}</span>
                  <div className="w-9 h-9 rounded-md bg-surface-alt border border-border-light flex items-center justify-center group-hover:border-accent/40 transition-colors">
                    <Icon className="w-4.5 h-4.5 text-text-mid" />
                  </div>
                </div>
                <h3 className="text-base font-semibold text-text mb-1.5">{title}</h3>
                <p className="text-sm text-text-muted leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
