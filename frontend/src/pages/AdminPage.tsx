import React, { useEffect, useState } from 'react';
import { 
  Shield, BarChart3, BookOpen, Layers, FileText, Activity, 
  CheckCircle, XCircle, Search, Edit3, Lock 
} from 'lucide-react';
import { apiClient } from '../api/client';
import { AdminMetrics } from '../types';

export const AdminPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'metrics' | 'resources' | 'skills' | 'content' | 'audit'>('metrics');
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [adminResources, setAdminResources] = useState<any[]>([]);
  const [adminSkills, setAdminSkills] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const m: any = await apiClient.get('/admin/metrics');
      setMetrics(m);

      const r: any = await apiClient.get('/admin/resources');
      setAdminResources(r || []);

      const s: any = await apiClient.get('/admin/skills');
      setAdminSkills(s || []);

      const logs: any = await apiClient.get('/admin/audit');
      setAuditLogs(logs || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleToggleVerification = async (resourceId: string, currentVerified: boolean) => {
    try {
      await apiClient.patch(`/admin/resources/${resourceId}?verified=${!currentVerified}`, {});
      setAdminResources(adminResources.map(res => res.id === resourceId ? { ...res, verified: !currentVerified } : res));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="w-full pt-20 pb-16 bg-surface min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <span className="text-xs uppercase tracking-wider text-primary font-bold block mb-1 flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-primary" /> Operational Admin Console
            </span>
            <h1 className="text-3xl font-extrabold text-on-surface">SkillAlpha System Operations</h1>
          </div>
          <span className="px-3 py-1 rounded-full bg-primary-fixed text-on-primary-fixed text-xs font-bold">
            Role: Admin
          </span>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-outline-variant/60 pb-4 mb-8 overflow-x-auto">
          {[
            { key: 'metrics', label: 'Dashboard Metrics', icon: BarChart3 },
            { key: 'resources', label: 'Resource Registry', icon: BookOpen },
            { key: 'skills', label: 'Skill Ontology Graph', icon: Layers },
            { key: 'content', label: 'CMS Content', icon: FileText },
            { key: 'audit', label: 'Audit Trail', icon: Activity }
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-colors whitespace-nowrap ${
                activeTab === key
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container-low'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* METRICS TAB */}
        {activeTab === 'metrics' && metrics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
              <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Active Learners</div>
              <div className="text-3xl font-extrabold text-on-surface">{metrics.active_users}</div>
            </div>
            <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
              <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Roadmaps Generated</div>
              <div className="text-3xl font-extrabold text-primary">{metrics.roadmaps_created}</div>
            </div>
            <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
              <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Resources Indexed</div>
              <div className="text-3xl font-extrabold text-on-surface">{metrics.resources_indexed}</div>
            </div>
            <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 p-5 shadow-sm">
              <div className="text-xs font-bold text-on-surface-variant uppercase mb-1">Positive Feedback</div>
              <div className="text-3xl font-extrabold text-secondary-container">{metrics.save_rate_percent}%</div>
            </div>
          </div>
        )}

        {/* RESOURCES TAB */}
        {activeTab === 'resources' && (
          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-outline-variant/40 font-bold text-sm text-on-surface">
              Resource Management & Verification
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-surface-container-low text-on-surface-variant font-bold border-b border-outline-variant/40">
                    <th className="p-3.5">Title</th>
                    <th className="p-3.5">Provider</th>
                    <th className="p-3.5">Type</th>
                    <th className="p-3.5">Quality Score</th>
                    <th className="p-3.5">Status</th>
                    <th className="p-3.5">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/30">
                  {adminResources.map((res) => (
                    <tr key={res.id} className="hover:bg-surface-container-low/40">
                      <td className="p-3.5 font-bold text-on-surface">{res.title}</td>
                      <td className="p-3.5 text-on-surface-variant">{res.provider}</td>
                      <td className="p-3.5"><span className="bg-surface-container px-2 py-0.5 rounded font-mono text-[10px]">{res.resource_type}</span></td>
                      <td className="p-3.5 font-bold text-primary">{(res.quality_score * 100).toFixed(0)}%</td>
                      <td className="p-3.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${res.verified ? 'bg-primary-fixed text-on-primary-fixed' : 'bg-error-container text-on-error-container'}`}>
                          {res.verified ? 'VERIFIED' : 'UNVERIFIED'}
                        </span>
                      </td>
                      <td className="p-3.5">
                        <button
                          onClick={() => handleToggleVerification(res.id, res.verified)}
                          className="px-3 py-1 rounded bg-surface-container-low hover:bg-surface-container font-semibold text-[11px]"
                        >
                          Toggle Verification
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* SKILLS TAB */}
        {activeTab === 'skills' && (
          <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/60 shadow-sm p-6">
            <h2 className="text-sm font-bold text-on-surface mb-4">Target Skill Ontology ({adminSkills.length} Nodes)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {adminSkills.map((sk) => (
                <div key={sk.id} className="p-4 rounded-xl bg-surface-container-low border border-outline-variant/40">
                  <div className="flex items-center justify-between font-bold text-sm text-on-surface mb-1">
                    <span>{sk.name}</span>
                    <span className="text-[10px] bg-primary-fixed/40 text-primary px-2 py-0.5 rounded uppercase">{sk.domain}</span>
                  </div>
                  <p className="text-xs text-on-surface-variant">{sk.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
