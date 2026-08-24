import { Module } from '@nestjs/common';

// Repositories (Data Layer)
import { ProductoExternoRepository, VentaRepository } from './repositories';

// Services
import { ProductoExternoService, VentaService } from './services';

// Controllers
import { ProductoExternoController, VentaController } from './controllers';

// Clients Mock
import { DatabaseModule } from '../datasources/database.module';
import { LogisticaModule } from '../logistica/logistica.module';
import { repositoryProviders } from './repositories/repository.providers';

import { IdentificacionModule } from '../identificacion/identificacion.module';

@Module({
  imports: [DatabaseModule, LogisticaModule, IdentificacionModule],
  controllers: [ProductoExternoController, VentaController],
  providers: [
    // Repositories
    ...repositoryProviders,
    ProductoExternoRepository,
    VentaRepository,
    // Services
    ProductoExternoService,
    VentaService,
  ],
  exports: [VentaService],
})
export class VentasModule {}
